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
 * Configure the fetch client with Django-friendly defaults:
 * - throws on non-2xx responses (so callers don't have to check the status)
 * - sends cookies on every request
 * - injects the CSRF token header on non-safe methods
 * - optionally enforces a per-request timeout via AbortSignal
 * - classifies fetch-level rejections into `TransportError` so that error
 *   interceptors can discriminate them from HTTP errors
 *
 * Call once at app startup, before any API calls and before registering
 * application error interceptors (so they receive the classified error).
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

    client.interceptors.error.use((error, response, request) => {
        if (!response && request && !(error instanceof TransportError)) {
            return new TransportError(classifyTransportError(error), request, error);
        }
        return error;
    });
}
