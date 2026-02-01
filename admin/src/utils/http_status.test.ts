import { describe, expect, it } from "vitest";

import { HttpStatus, isHttpError } from "./http_status";

describe("HttpStatus constants", () => {
    it("should have correct status code values", () => {
        expect(HttpStatus.OK).toBe(200);
        expect(HttpStatus.CREATED).toBe(201);
        expect(HttpStatus.NO_CONTENT).toBe(204);
        expect(HttpStatus.BAD_REQUEST).toBe(400);
        expect(HttpStatus.UNAUTHORIZED).toBe(401);
        expect(HttpStatus.FORBIDDEN).toBe(403);
        expect(HttpStatus.NOT_FOUND).toBe(404);
        expect(HttpStatus.CONFLICT).toBe(409);
        expect(HttpStatus.TEAPOT).toBe(418);
        expect(HttpStatus.INTERNAL_SERVER_ERROR).toBe(500);
        expect(HttpStatus.BAD_GATEWAY).toBe(502);
        expect(HttpStatus.SERVICE_UNAVAILABLE).toBe(503);
        expect(HttpStatus.GATEWAY_TIMEOUT).toBe(504);
    });
});

describe("isHttpError", () => {
    describe("matching status codes", () => {
        it("should return true for matching 400 status", () => {
            const error = { response: { status: 400 } };
            expect(isHttpError(error, HttpStatus.BAD_REQUEST)).toBe(true);
        });

        it("should return true for matching 404 status", () => {
            const error = { response: { status: 404 } };
            expect(isHttpError(error, HttpStatus.NOT_FOUND)).toBe(true);
        });

        it("should return true for matching 500 status", () => {
            const error = { response: { status: 500 } };
            expect(isHttpError(error, HttpStatus.INTERNAL_SERVER_ERROR)).toBe(true);
        });
    });

    describe("non-matching status codes", () => {
        it("should return false for non-matching status", () => {
            const error = { response: { status: 400 } };
            expect(isHttpError(error, HttpStatus.NOT_FOUND)).toBe(false);
        });

        it("should return false for different 4xx status", () => {
            const error = { response: { status: 403 } };
            expect(isHttpError(error, HttpStatus.UNAUTHORIZED)).toBe(false);
        });
    });

    describe("edge cases", () => {
        it("should return false for null error", () => {
            expect(isHttpError(null, HttpStatus.BAD_REQUEST)).toBe(false);
        });

        it("should return false for undefined error", () => {
            expect(isHttpError(undefined, HttpStatus.BAD_REQUEST)).toBe(false);
        });

        it("should return false for error without response", () => {
            const error = {};
            expect(isHttpError(error, HttpStatus.BAD_REQUEST)).toBe(false);
        });

        it("should return false for error with null response", () => {
            const error = { response: null };
            expect(isHttpError(error, HttpStatus.BAD_REQUEST)).toBe(false);
        });

        it("should return false for error with missing status", () => {
            const error = { response: {} };
            expect(isHttpError(error, HttpStatus.BAD_REQUEST)).toBe(false);
        });
    });
});
