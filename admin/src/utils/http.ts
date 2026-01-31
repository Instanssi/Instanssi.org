import type { AxiosError } from "axios";
import { camelCase } from "lodash-es";

import { HttpStatus } from "@/utils/http_status";

type FieldErrors = Record<string, string>;
type SetErrorsFn = (errors: FieldErrors) => void;
type ToastInterface = { error: (message: string) => void };
type FieldMapping = Record<string, string>;

/**
 * Extract error message from API error response.
 * Returns the detail message if available, otherwise the fallback.
 */
export function getApiErrorMessage(error: unknown, fallbackMessage: string): string {
    const axiosError = error as AxiosError;
    if (axiosError?.response?.data) {
        const data = axiosError.response.data as Record<string, unknown>;
        if (typeof data.detail === "string") {
            return data.detail;
        }
    }
    return fallbackMessage;
}

/**
 * Handle API errors by mapping field-level validation errors to form fields
 * and showing appropriate toast messages.
 *
 * @param error - The caught error (typically AxiosError)
 * @param setErrors - vee-validate's setErrors function
 * @param toast - Toast interface with error() method
 * @param fallbackMessage - Message to show if no specific error can be extracted
 * @param fieldMapping - Optional mapping from API field names to form field names
 */
export function handleApiError(
    error: unknown,
    setErrors: SetErrorsFn,
    toast: ToastInterface,
    fallbackMessage: string,
    fieldMapping: FieldMapping = {}
): void {
    const axiosError = error as AxiosError;

    if (axiosError?.response) {
        const status = axiosError.response.status;
        const data = axiosError.response.data as Record<string, unknown>;

        // Handle field-level validation errors (400 Bad Request)
        if (status === HttpStatus.BAD_REQUEST && typeof data === "object" && data !== null) {
            const fieldErrors: FieldErrors = {};
            let hasFieldErrors = false;

            for (const [key, value] of Object.entries(data)) {
                if (key !== "detail" && Array.isArray(value)) {
                    // Apply custom mapping first, then snake_case conversion
                    const fieldName = fieldMapping[key] ?? camelCase(key);
                    fieldErrors[fieldName] = value.join(", ");
                    hasFieldErrors = true;
                }
            }

            if (hasFieldErrors) {
                setErrors(fieldErrors);
                return;
            }
        }

        // Check for detail message
        if (data && typeof data.detail === "string") {
            toast.error(data.detail);
            return;
        }
    }

    // Fallback to generic message
    toast.error(fallbackMessage);
    console.error(error);
}
