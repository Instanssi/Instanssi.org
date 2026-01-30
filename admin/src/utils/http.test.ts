import type { AxiosError } from "axios";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { handleApiError } from "./http";

describe("handleApiError", () => {
    const mockSetErrors = vi.fn();
    const mockToast = { error: vi.fn() };
    const fallbackMessage = "Something went wrong";

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("field validation errors (400)", () => {
        it("should map field errors to form fields", () => {
            const error = {
                response: {
                    status: 400,
                    data: {
                        username: ["This field is required."],
                        email: ["Enter a valid email address."],
                    },
                },
            } as AxiosError;

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockSetErrors).toHaveBeenCalledWith({
                username: "This field is required.",
                email: "Enter a valid email address.",
            });
            expect(mockToast.error).not.toHaveBeenCalled();
        });

        it("should convert snake_case field names to camelCase", () => {
            const error = {
                response: {
                    status: 400,
                    data: {
                        first_name: ["Too long."],
                        last_name: ["Required."],
                    },
                },
            } as AxiosError;

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockSetErrors).toHaveBeenCalledWith({
                firstName: "Too long.",
                lastName: "Required.",
            });
        });

        it("should use custom field mapping when provided", () => {
            const error = {
                response: {
                    status: 400,
                    data: {
                        mainurl: ["Enter a valid URL."],
                    },
                },
            } as AxiosError;

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage, {
                mainurl: "mainUrl",
            });

            expect(mockSetErrors).toHaveBeenCalledWith({
                mainUrl: "Enter a valid URL.",
            });
        });

        it("should join multiple error messages for a field", () => {
            const error = {
                response: {
                    status: 400,
                    data: {
                        password: ["Too short.", "Must contain a number."],
                    },
                },
            } as AxiosError;

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockSetErrors).toHaveBeenCalledWith({
                password: "Too short., Must contain a number.",
            });
        });

        it("should not show toast when field errors are present", () => {
            const error = {
                response: {
                    status: 400,
                    data: {
                        name: ["Required."],
                    },
                },
            } as AxiosError;

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockToast.error).not.toHaveBeenCalled();
        });
    });

    describe("detail message errors", () => {
        it("should show detail message in toast", () => {
            const error = {
                response: {
                    status: 400,
                    data: {
                        detail: "You do not have permission to perform this action.",
                    },
                },
            } as AxiosError;

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockToast.error).toHaveBeenCalledWith(
                "You do not have permission to perform this action."
            );
            expect(mockSetErrors).not.toHaveBeenCalled();
        });

        it("should prefer field errors over detail message", () => {
            const error = {
                response: {
                    status: 400,
                    data: {
                        detail: "Validation failed.",
                        name: ["Required."],
                    },
                },
            } as AxiosError;

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockSetErrors).toHaveBeenCalledWith({
                name: "Required.",
            });
            expect(mockToast.error).not.toHaveBeenCalled();
        });
    });

    describe("fallback behavior", () => {
        it("should show fallback message for non-400 errors", () => {
            const error = {
                response: {
                    status: 500,
                    data: {},
                },
            } as AxiosError;

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockToast.error).toHaveBeenCalledWith(fallbackMessage);
        });

        it("should show fallback message when no response", () => {
            const error = {} as AxiosError;

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockToast.error).toHaveBeenCalledWith(fallbackMessage);
        });

        it("should show fallback message for 400 with no parseable data", () => {
            const error = {
                response: {
                    status: 400,
                    data: "Bad Request",
                },
            } as AxiosError;

            handleApiError(error, mockSetErrors, mockToast, fallbackMessage);

            expect(mockToast.error).toHaveBeenCalledWith(fallbackMessage);
        });
    });
});
