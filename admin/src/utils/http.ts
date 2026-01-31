import { HttpStatus } from "@/utils/http_status";

type FieldErrors = Record<string, string>;
type SetErrorsFn = (errors: FieldErrors) => void;
type ToastInterface = { error: (message: string) => void };
type FieldMapping = Record<string, string>;

interface ErrorResponse {
    status: number;
    data: unknown;
}

function getErrorResponse(error: unknown): ErrorResponse | null {
    const err = error as { response?: ErrorResponse };
    return err?.response ?? null;
}

function getResponseData(response: ErrorResponse): Record<string, unknown> | null {
    const { data } = response;
    return typeof data === "object" && data !== null ? (data as Record<string, unknown>) : null;
}

/**
 * Extract error message from API error response.
 * Returns the detail message if available, otherwise the fallback.
 */
export function getApiErrorMessage(error: unknown, fallbackMessage: string): string {
    const response = getErrorResponse(error);
    const data = response && getResponseData(response);
    if (data && typeof data.detail === "string") {
        return data.detail;
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
 * @param fieldMapping - Mapping from API field names to form field names.
 *        Only explicitly mapped fields will show errors on form fields.
 *        Unmapped field errors are shown in a toast.
 */
export function handleApiError(
    error: unknown,
    setErrors: SetErrorsFn,
    toast: ToastInterface,
    fallbackMessage: string,
    fieldMapping: FieldMapping = {}
): void {
    const response = getErrorResponse(error);
    if (!response) {
        toast.error(fallbackMessage);
        console.error(error);
        return;
    }

    const data = getResponseData(response);

    // Handle field-level validation errors (400 Bad Request)
    if (response.status === HttpStatus.BAD_REQUEST && data) {
        const fieldErrors: FieldErrors = {};
        const toastMessages: string[] = [];

        for (const [key, value] of Object.entries(data)) {
            if (key === "detail" || !Array.isArray(value)) continue;

            const message = value.join(", ");
            const mappedField = fieldMapping[key];

            if (mappedField) {
                fieldErrors[mappedField] = message;
            } else {
                toastMessages.push(`${key}: ${message}`);
            }
        }

        const hasFieldErrors = Object.keys(fieldErrors).length > 0;
        const hasToastMessages = toastMessages.length > 0;

        if (hasFieldErrors || hasToastMessages) {
            if (hasFieldErrors) setErrors(fieldErrors);
            if (hasToastMessages) toast.error(toastMessages.join("\n"));
            return;
        }
    }

    // Check for detail message
    if (data && typeof data.detail === "string") {
        toast.error(data.detail);
        return;
    }

    toast.error(fallbackMessage);
    console.error(error);
}
