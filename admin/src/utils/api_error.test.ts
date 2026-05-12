import { ApiError, HttpStatus, isHttpError } from "@instanssi/api";
import { describe, expect, it } from "vitest";

describe("ApiError", () => {
    it("captures status and data from the response", () => {
        const response = new Response(null, { status: 418 });
        const request = new Request("http://test.local/");
        const error = new ApiError({ message: "boom" }, response, request);

        expect(error.response.status).toBe(418);
        expect(error.response.data).toEqual({ message: "boom" });
    });

    it("retains the originating Request", () => {
        const response = new Response(null, { status: 500 });
        const request = new Request("http://test.local/foo");
        const error = new ApiError(null, response, request);

        expect(error.request.url).toBe("http://test.local/foo");
    });

    it("is an Error instance with a useful message and name", () => {
        const response = new Response(null, { status: 404 });
        const request = new Request("http://test.local/");
        const error = new ApiError({}, response, request);

        expect(error).toBeInstanceOf(Error);
        expect(error.name).toBe("ApiError");
        expect(error.message).toBe("HTTP 404");
    });

    it("supports unknown body types (strings, objects, null)", () => {
        const response = new Response(null, { status: 500 });
        const request = new Request("http://test.local/");

        expect(new ApiError("text body", response, request).response.data).toBe("text body");
        expect(new ApiError(null, response, request).response.data).toBeNull();
        expect(new ApiError({ a: 1 }, response, request).response.data).toEqual({ a: 1 });
    });
});

describe("isHttpError", () => {
    function makeError(status: number): ApiError {
        return new ApiError({}, new Response(null, { status }), new Request("http://test.local/"));
    }

    it("returns true when error is ApiError with matching status", () => {
        expect(isHttpError(makeError(403), HttpStatus.FORBIDDEN)).toBe(true);
        expect(isHttpError(makeError(404), HttpStatus.NOT_FOUND)).toBe(true);
    });

    it("returns false when status differs", () => {
        expect(isHttpError(makeError(404), HttpStatus.FORBIDDEN)).toBe(false);
    });

    it("returns false for non-ApiError values", () => {
        expect(isHttpError(new Error("plain"), HttpStatus.FORBIDDEN)).toBe(false);
        expect(isHttpError({ response: { status: 403 } }, HttpStatus.FORBIDDEN)).toBe(false);
        expect(isHttpError(null, HttpStatus.FORBIDDEN)).toBe(false);
        expect(isHttpError(undefined, HttpStatus.FORBIDDEN)).toBe(false);
        expect(isHttpError("nope", HttpStatus.FORBIDDEN)).toBe(false);
    });
});
