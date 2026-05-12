/**
 * Structured error thrown by the API client when a request returns a non-2xx
 * response. Mirrors the `.response.status` / `.response.data` access shape the
 * codebase already uses, so consumers can read fields directly without
 * unwrapping.
 */
export class ApiError<TData = unknown> extends Error {
    public readonly response: { status: number; data: TData };
    public readonly request: Request;

    constructor(data: TData, response: Response, request: Request) {
        super(`HTTP ${response.status}`);
        this.name = "ApiError";
        this.response = { status: response.status, data };
        this.request = request;
    }
}

/**
 * Categorical kind of a transport-level failure — distinguishes
 * AbortSignal.timeout from caller-initiated aborts from raw network failures.
 */
export type TransportErrorKind = "timeout" | "abort" | "network";

/**
 * Thrown when the request never produced an HTTP response — i.e. fetch itself
 * rejected. Sibling of ApiError; callers can disambiguate the two kinds of
 * failure with `instanceof`. The original rejection is kept on `.cause`.
 */
export class TransportError extends Error {
    public readonly kind: TransportErrorKind;
    public readonly request: Request;
    public readonly cause: unknown;

    constructor(kind: TransportErrorKind, request: Request, cause: unknown) {
        super(`Transport error: ${kind}`);
        this.name = "TransportError";
        this.kind = kind;
        this.request = request;
        this.cause = cause;
    }
}

export function classifyTransportError(err: unknown): TransportErrorKind {
    if (err instanceof DOMException) {
        if (err.name === "TimeoutError") return "timeout";
        if (err.name === "AbortError") return "abort";
    }
    return "network";
}

export function isHttpError(error: unknown, status: number): boolean {
    return error instanceof ApiError && error.response.status === status;
}
