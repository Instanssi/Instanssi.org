import type { Client } from "./generated/client";
import { TransportError, classifyTransportError } from "./error";

export interface ConfigureClientOptions {
    /** Per-request timeout in milliseconds, applied via AbortSignal.timeout. */
    timeout?: number;
    /** Cookie name to read the CSRF token from. Default "csrftoken" (Django). */
    csrfCookieName?: string;
    /** Header name to send the CSRF token in. Default "X-CSRFToken" (Django). */
    csrfHeaderName?: string;
}

const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

function readCookie(name: string): string | null {
    if (typeof document === "undefined") return null;
    const prefix = `${encodeURIComponent(name)}=`;
    for (const part of document.cookie.split("; ")) {
        if (part.startsWith(prefix)) {
            return decodeURIComponent(part.slice(prefix.length));
        }
    }
    return null;
}

/**
 * Run the registered error interceptors with a transport-level rejection.
 * A sentinel Response is supplied to satisfy the interceptor signature;
 * consumers discriminate the case via `instanceof TransportError`.
 */
async function runErrorChain(
    client: Client,
    transportError: TransportError,
    request: Request
): Promise<unknown> {
    const sentinelResponse = new Response(null, { status: 0, statusText: "Transport error" });
    let finalError: unknown = transportError;
    for (const fn of client.interceptors.error.fns) {
        if (fn) {
            finalError = await fn(
                transportError,
                sentinelResponse,
                request,
                {} as Parameters<typeof fn>[3]
            );
        }
    }
    return finalError;
}

/**
 * Configure the fetch client with Django-friendly defaults:
 * - throws on non-2xx responses (so callers don't have to check the status)
 * - sends cookies on every request
 * - injects the CSRF token header on non-safe methods
 * - optionally enforces a per-request timeout via AbortSignal
 * - classifies fetch-level rejections into `TransportError` and routes them
 *   through `client.interceptors.error` alongside HTTP errors
 *
 * Call once at app startup, before any API calls.
 */
export function configureClient(client: Client, options: ConfigureClientOptions = {}): void {
    const csrfCookieName = options.csrfCookieName ?? "csrftoken";
    const csrfHeaderName = options.csrfHeaderName ?? "X-CSRFToken";
    const timeout = options.timeout;

    client.setConfig({ throwOnError: true, credentials: "include" });

    client.interceptors.request.use((request) => {
        let next = request;

        if (timeout !== undefined) {
            const signal = AbortSignal.any([next.signal, AbortSignal.timeout(timeout)]);
            next = new Request(next, { signal });
        }

        if (!SAFE_METHODS.has(next.method)) {
            const token = readCookie(csrfCookieName);
            if (token && !next.headers.has(csrfHeaderName)) {
                next.headers.set(csrfHeaderName, token);
            }
        }

        return next;
    });

    const baseFetch = client.getConfig().fetch ?? globalThis.fetch;
    const wrappedFetch: typeof fetch = async (input, init) => {
        try {
            return await baseFetch(input, init);
        } catch (err) {
            // The generated client always invokes fetch with a Request, so this branch
            // is just a type-safety belt for non-Request callers (none in practice).
            const request = input instanceof Request ? input : new Request(input, init);
            const transportError = new TransportError(classifyTransportError(err), request, err);
            throw await runErrorChain(client, transportError, request);
        }
    };
    client.setConfig({ fetch: wrappedFetch });
}
