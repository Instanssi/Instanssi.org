import { TransportError, configureClient, createClient } from "@instanssi/api";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// The fetch client always invokes the configured `fetch` with a Request object;
// this narrower stub signature makes the test bodies more pleasant.
type FetchFn = (request: Request) => Promise<Response>;

function clearCookies(): void {
    for (const part of document.cookie.split("; ")) {
        const name = part.split("=")[0];
        if (name) {
            document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
        }
    }
}

/**
 * Build a fresh client with a custom fetch stub so interceptors don't leak
 * across tests. The fetch stub is installed before `configureClient` so the
 * `onFetchError` wrap (which composes around the configured fetch) can see it.
 */
function makeClient(
    fetchFn: FetchFn,
    options: Parameters<typeof configureClient>[1] = {}
): ReturnType<typeof createClient> {
    const client = createClient();
    client.setConfig({ baseUrl: "http://test.local", fetch: fetchFn as typeof fetch });
    configureClient(client, options);
    return client;
}

describe("configureClient", () => {
    beforeEach(() => clearCookies());
    afterEach(() => clearCookies());

    describe("CSRF injection", () => {
        it("adds X-CSRFToken header on non-safe methods when the cookie is present", async () => {
            document.cookie = "csrftoken=token-abc";
            let captured: Request | undefined;
            const client = makeClient(async (req) => {
                captured = req;
                return new Response(null, { status: 204 });
            });

            await client.post({ url: "/x" });

            expect(captured?.headers.get("X-CSRFToken")).toBe("token-abc");
        });

        it("does not add the header on GET requests", async () => {
            document.cookie = "csrftoken=token-abc";
            let captured: Request | undefined;
            const client = makeClient(async (req) => {
                captured = req;
                return new Response(null, { status: 200 });
            });

            await client.get({ url: "/x" });

            expect(captured?.headers.get("X-CSRFToken")).toBeNull();
        });

        it("does not add the header when the cookie is missing", async () => {
            let captured: Request | undefined;
            const client = makeClient(
                async (req) => {
                    captured = req;
                    return new Response(null, { status: 204 });
                },
                // Point at a cookie name that no other test sets so we
                // don't depend on happy-dom honoring cookie expiration.
                { csrfCookieName: "definitely-not-set-anywhere" }
            );

            await client.post({ url: "/x" });

            expect(captured?.headers.get("X-CSRFToken")).toBeNull();
        });

        it("honors a custom cookie/header name", async () => {
            document.cookie = "custom_csrf=token-xyz";
            let captured: Request | undefined;
            const client = makeClient(
                async (req) => {
                    captured = req;
                    return new Response(null, { status: 204 });
                },
                { csrfCookieName: "custom_csrf", csrfHeaderName: "X-Custom-CSRF" }
            );

            await client.put({ url: "/x" });

            expect(captured?.headers.get("X-Custom-CSRF")).toBe("token-xyz");
            expect(captured?.headers.get("X-CSRFToken")).toBeNull();
        });

        it("does not overwrite a caller-supplied CSRF header", async () => {
            document.cookie = "csrftoken=token-from-cookie";
            let captured: Request | undefined;
            const client = makeClient(async (req) => {
                captured = req;
                return new Response(null, { status: 204 });
            });

            await client.post({ url: "/x", headers: { "X-CSRFToken": "caller-supplied" } });

            expect(captured?.headers.get("X-CSRFToken")).toBe("caller-supplied");
        });
    });

    describe("timeout", () => {
        it("aborts a slow request after the configured timeout", async () => {
            const client = makeClient(
                (req) =>
                    new Promise<Response>((_, reject) => {
                        req.signal.addEventListener("abort", () =>
                            reject(req.signal.reason ?? new Error("aborted"))
                        );
                    }),
                { timeout: 25 }
            );

            await expect(client.get({ url: "/x" })).rejects.toBeDefined();
        });

        it("runs registered error interceptors with a TransportError(kind=timeout) when AbortSignal.timeout fires", async () => {
            const errInterceptor = vi.fn((err: unknown) => err);
            const client = makeClient(
                (req) =>
                    new Promise<Response>((_, reject) => {
                        req.signal.addEventListener("abort", () =>
                            reject(req.signal.reason ?? new Error("aborted"))
                        );
                    }),
                { timeout: 25 }
            );
            client.interceptors.error.use(errInterceptor);

            await expect(client.get({ url: "/x" })).rejects.toBeInstanceOf(TransportError);

            expect(errInterceptor).toHaveBeenCalledOnce();
            const transportError = errInterceptor.mock.calls[0]![0] as TransportError;
            expect(transportError).toBeInstanceOf(TransportError);
            expect(transportError.kind).toBe("timeout");
            expect(transportError.cause).toBeInstanceOf(DOMException);
            expect((transportError.cause as DOMException).name).toBe("TimeoutError");
            expect(transportError.request).toBeInstanceOf(Request);
        });

        it("preserves a caller-supplied AbortSignal alongside the timeout", async () => {
            const controller = new AbortController();
            let capturedSignal: AbortSignal | undefined;
            const client = makeClient(
                (req) =>
                    new Promise<Response>((_, reject) => {
                        capturedSignal = req.signal;
                        if (req.signal.aborted) {
                            reject(req.signal.reason ?? new Error("aborted"));
                            return;
                        }
                        req.signal.addEventListener("abort", () =>
                            reject(req.signal.reason ?? new Error("aborted"))
                        );
                    }),
                { timeout: 5000 }
            );

            const pending = client.get({ url: "/x", signal: controller.signal });
            // Yield once so the request interceptor runs and composes the signal,
            // then abort via the caller's controller.
            await Promise.resolve();
            controller.abort(new Error("user cancelled"));

            await expect(pending).rejects.toBeDefined();
            expect(capturedSignal?.aborted).toBe(true);
        });
    });

    describe("transport errors", () => {
        it("classifies a network-level TypeError as kind=network and preserves it on .cause", async () => {
            const original = new TypeError("Failed to fetch");
            const errInterceptor = vi.fn((err: unknown) => err);
            const client = makeClient(async () => {
                throw original;
            });
            client.interceptors.error.use(errInterceptor);

            const promise = client.get({ url: "/x" });
            await expect(promise).rejects.toBeInstanceOf(TransportError);
            const thrown = await promise.catch((e) => e);
            expect((thrown as TransportError).kind).toBe("network");
            expect((thrown as TransportError).cause).toBe(original);

            expect(errInterceptor).toHaveBeenCalledOnce();
            expect((errInterceptor.mock.calls[0]![0] as TransportError).cause).toBe(original);
        });

        it("classifies an AbortError as kind=abort", async () => {
            const errInterceptor = vi.fn((err: unknown) => err);
            const client = makeClient(async () => {
                throw new DOMException("cancelled", "AbortError");
            });
            client.interceptors.error.use(errInterceptor);

            await expect(client.get({ url: "/x" })).rejects.toBeInstanceOf(TransportError);
            expect((errInterceptor.mock.calls[0]![0] as TransportError).kind).toBe("abort");
        });

        it("wraps even when no error interceptor is registered", async () => {
            const client = makeClient(async () => {
                throw new TypeError("Failed to fetch");
            });

            await expect(client.get({ url: "/x" })).rejects.toBeInstanceOf(TransportError);
        });

        it("the thrown error reflects the interceptor's return value", async () => {
            const replacement = new Error("replaced");
            const client = makeClient(async () => {
                throw new TypeError("Failed to fetch");
            });
            client.interceptors.error.use(() => replacement);

            await expect(client.get({ url: "/x" })).rejects.toBe(replacement);
        });

        it("does not invoke the error interceptor on successful responses", async () => {
            const errInterceptor = vi.fn((err: unknown) => err);
            const client = makeClient(async () => new Response(null, { status: 204 }));
            client.interceptors.error.use(errInterceptor);

            await client.get({ url: "/x" });

            expect(errInterceptor).not.toHaveBeenCalled();
        });
    });
});
