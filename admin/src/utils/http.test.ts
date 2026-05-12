import { beforeEach, describe, expect, it, vi } from "vitest";

import { createMockApiError } from "@/test/helpers/form-test-utils";
import { getApiErrorMessage, handleApiError } from "./http";

describe("handleApiError", () => {
    const mockSetErrors = vi.fn();
    const mockToast = { error: vi.fn() };
    const fallbackMessage = "Something went wrong";

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("field validation errors (400)", () => {
        it("should map field errors to form fields using explicit mapping", () => {
            const error = createMockApiError(400, {
                username: ["This field is required."],
                email: ["Enter a valid email address."],
            });

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage, {
                username: "username",
                email: "email",
            });

            expect(mockSetErrors).toHaveBeenCalledWith({
                username: "This field is required.",
                email: "Enter a valid email address.",
            });
            expect(mockToast.error).not.toHaveBeenCalled();
        });

        it("should show unmapped field errors in toast", () => {
            const error = createMockApiError(400, {
                first_name: ["Too long."],
                last_name: ["Required."],
            });

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockSetErrors).not.toHaveBeenCalled();
            expect(mockToast.error).toHaveBeenCalledWith(
                "first_name: Too long.\nlast_name: Required."
            );
        });

        it("should use custom field mapping", () => {
            const error = createMockApiError(400, {
                first_name: ["Too long."],
                last_name: ["Required."],
            });

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage, {
                first_name: "firstName",
                last_name: "lastName",
            });

            expect(mockSetErrors).toHaveBeenCalledWith({
                firstName: "Too long.",
                lastName: "Required.",
            });
            expect(mockToast.error).not.toHaveBeenCalled();
        });

        it("should join multiple error messages for a field", () => {
            const error = createMockApiError(400, {
                password: ["Too short.", "Must contain a number."],
            });

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage, {
                password: "password",
            });

            expect(mockSetErrors).toHaveBeenCalledWith({
                password: "Too short., Must contain a number.",
            });
        });

        it("should show both field errors and toast for mixed mapped/unmapped", () => {
            const error = createMockApiError(400, {
                name: ["Required."],
                unknown_field: ["Some error."],
            });

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage, {
                name: "name",
            });

            expect(mockSetErrors).toHaveBeenCalledWith({
                name: "Required.",
            });
            expect(mockToast.error).toHaveBeenCalledWith("unknown_field: Some error.");
        });
    });

    describe("detail message errors", () => {
        it("should show detail message in toast", () => {
            const error = createMockApiError(400, {
                detail: "You do not have permission to perform this action.",
            });

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockToast.error).toHaveBeenCalledWith(
                "You do not have permission to perform this action."
            );
            expect(mockSetErrors).not.toHaveBeenCalled();
        });

        it("should prefer field errors over detail message", () => {
            const error = createMockApiError(400, {
                detail: "Validation failed.",
                name: ["Required."],
            });

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage, {
                name: "name",
            });

            expect(mockSetErrors).toHaveBeenCalledWith({
                name: "Required.",
            });
            expect(mockToast.error).not.toHaveBeenCalled();
        });
    });

    describe("fallback behavior", () => {
        it("should show fallback message for non-400 errors", () => {
            const error = createMockApiError(500, {});

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockToast.error).toHaveBeenCalledWith(fallbackMessage);
        });

        it("should show fallback message when error is not an ApiError", () => {
            handleApiError({}, mockSetErrors, mockToast, fallbackMessage);

            expect(mockToast.error).toHaveBeenCalledWith(fallbackMessage);
        });

        it("should show fallback message for 400 with non-object data", () => {
            const error = createMockApiError(400, "Bad Request");

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockToast.error).toHaveBeenCalledWith(fallbackMessage);
        });
    });
});

describe("getApiErrorMessage", () => {
    const fallbackMessage = "Default error message";

    describe("with detail message present", () => {
        it("should return detail message from response", () => {
            const error = createMockApiError(400, { detail: "Custom error from server" });
            expect(getApiErrorMessage(error, fallbackMessage)).toBe("Custom error from server");
        });

        it("should return detail for any status code", () => {
            const error = createMockApiError(500, { detail: "Internal server error details" });
            expect(getApiErrorMessage(error, fallbackMessage)).toBe(
                "Internal server error details"
            );
        });
    });

    describe("fallback behavior", () => {
        it("should return fallback when no detail present", () => {
            const error = createMockApiError(400, { name: ["Required"] });
            expect(getApiErrorMessage(error, fallbackMessage)).toBe(fallbackMessage);
        });

        it("should return fallback when response data is not an object", () => {
            const error = createMockApiError(400, "Plain text error");
            expect(getApiErrorMessage(error, fallbackMessage)).toBe(fallbackMessage);
        });

        it("should return fallback when error is not an ApiError", () => {
            expect(getApiErrorMessage({}, fallbackMessage)).toBe(fallbackMessage);
        });

        it("should return fallback for null error", () => {
            expect(getApiErrorMessage(null, fallbackMessage)).toBe(fallbackMessage);
        });

        it("should return fallback when detail is not a string", () => {
            const error = createMockApiError(400, { detail: 123 });
            expect(getApiErrorMessage(error, fallbackMessage)).toBe(fallbackMessage);
        });
    });
});
