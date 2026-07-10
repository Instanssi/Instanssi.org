import { ApiError, TransportError } from "@instanssi/api";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { errorResponseInterceptor } from "./interceptors";

const toastErrorMock = vi.fn();
const toastWarningMock = vi.fn();

vi.mock("vue-toastification", () => ({
    useToast: () => ({
        success: vi.fn(),
        error: toastErrorMock,
        warning: toastWarningMock,
        info: vi.fn(),
    }),
}));

vi.mock("@/i18n", () => ({
    i18n: { global: { locale: { value: "en" }, t: (key: string) => key } },
    SUPPORTED_LOCALES: ["en", "fi"],
    isSupportedLocale: (v: string) => ["en", "fi"].includes(v),
    setLocale: vi.fn(),
}));

vi.mock("@sentry/vue", () => ({ captureException: vi.fn() }));

function makeRequest(path = "/some/endpoint/"): Request {
    return new Request(`http://test.local${path}`);
}

function makeResponse(status: number): Response {
    return new Response(null, { status });
}

beforeEach(() => {
    toastErrorMock.mockClear();
    toastWarningMock.mockClear();
});

describe("errorResponseInterceptor (transport branch)", () => {
    function transport(kind: "timeout" | "abort" | "network"): TransportError {
        return new TransportError(kind, makeRequest(), new Error("underlying"));
    }

    it("returns the TransportError unchanged for kind=timeout and toasts timeout", () => {
        const err = transport("timeout");
        const result = errorResponseInterceptor(err, undefined, err.request);
        expect(result).toBe(err);
        expect(toastErrorMock).toHaveBeenCalledWith("Toasts.errors.timeout");
    });

    it("toasts generic for kind=network", () => {
        const err = transport("network");
        errorResponseInterceptor(err, undefined, err.request);
        expect(toastErrorMock).toHaveBeenCalledWith("Toasts.errors.generic");
    });

    it("stays silent for kind=abort", () => {
        const err = transport("abort");
        errorResponseInterceptor(err, undefined, err.request);
        expect(toastErrorMock).not.toHaveBeenCalled();
        expect(toastWarningMock).not.toHaveBeenCalled();
    });
});

describe("errorResponseInterceptor (no response, unclassified)", () => {
    it("passes an unclassified error through unchanged without toasting", () => {
        const err = new Error("request building failed");
        const result = errorResponseInterceptor(err, undefined, undefined);
        expect(result).toBe(err);
        expect(toastErrorMock).not.toHaveBeenCalled();
        expect(toastWarningMock).not.toHaveBeenCalled();
    });
});

describe("errorResponseInterceptor (HTTP branch)", () => {
    it("wraps a 500 response into an ApiError and toasts ise", () => {
        const result = errorResponseInterceptor(
            { detail: "boom" },
            makeResponse(500),
            makeRequest()
        );
        expect(result).toBeInstanceOf(ApiError);
        expect((result as ApiError).response.status).toBe(500);
        expect(toastErrorMock).toHaveBeenCalledWith("Toasts.errors.ise");
    });

    it("does not toast on 400 (validation errors handled per-form)", () => {
        const result = errorResponseInterceptor(
            { field: ["bad"] },
            makeResponse(400),
            makeRequest()
        );
        expect(result).toBeInstanceOf(ApiError);
        expect(toastErrorMock).not.toHaveBeenCalled();
    });

    it("does not toast on auth-service-owned endpoints", () => {
        errorResponseInterceptor(
            { detail: "no" },
            makeResponse(401),
            makeRequest("/api/v2/user_info/")
        );
        expect(toastErrorMock).not.toHaveBeenCalled();
    });

    it("warns on 418", () => {
        errorResponseInterceptor({ detail: "tea" }, makeResponse(418), makeRequest());
        expect(toastWarningMock).toHaveBeenCalledWith("Toasts.errors.teapot");
    });

    it("toasts gateway on 502/503/504", () => {
        errorResponseInterceptor({}, makeResponse(503), makeRequest());
        expect(toastErrorMock).toHaveBeenCalledWith("Toasts.errors.gateway");
    });
});
