import * as Sentry from "@sentry/vue";
import { ApiError, HttpStatus, TransportError } from "@instanssi/api";
import { useToast } from "vue-toastification";

import { i18n } from "@/i18n";

export function errorResponseInterceptor(
    error: unknown,
    response: Response | undefined,
    request: Request | undefined
): unknown {
    if (error instanceof TransportError) {
        return handleTransportError(error);
    }
    if (!response || !request) {
        Sentry.captureException(error);
        return error;
    }
    return handleApiError(error, response, request);
}

function handleTransportError(error: TransportError): TransportError {
    Sentry.captureException(error);
    if (error.kind === "abort") {
        // User-initiated cancellation — stay silent.
        return error;
    }
    const toast = useToast();
    const { t } = i18n.global;
    toast.error(error.kind === "timeout" ? t("Toasts.errors.timeout") : t("Toasts.errors.generic"));
    return error;
}

function handleApiError(error: unknown, response: Response, request: Request): ApiError {
    const apiError = new ApiError(error, response, request);
    Sentry.captureException(apiError);

    // Don't worry about these paths -- they are handled by the auth service.
    const path = new URL(request.url).pathname;
    if (path.endsWith("/user_info/") || path.endsWith("/auth/login/")) {
        return apiError;
    }

    const toast = useToast();
    const { t } = i18n.global;
    switch (response.status) {
        case HttpStatus.BAD_REQUEST:
            // Validation errors - let the caller handle these via handleApiError
            break;

        case HttpStatus.UNAUTHORIZED:
            toast.error(t("Toasts.errors.sessionTimedOut"));
            break;

        case HttpStatus.CONFLICT:
            toast.error(t("Toasts.errors.conflict"));
            break;

        case HttpStatus.TEAPOT:
            // Mostly for testing :)
            toast.warning(t("Toasts.errors.teapot"));
            break;

        case HttpStatus.INTERNAL_SERVER_ERROR:
            // Something is badly wrong server-side
            toast.error(t("Toasts.errors.ise"));
            break;

        case HttpStatus.BAD_GATEWAY:
        case HttpStatus.SERVICE_UNAVAILABLE:
        case HttpStatus.GATEWAY_TIMEOUT:
            // These usually happen if server is down for maintenance etc.
            toast.error(t("Toasts.errors.gateway"));
            break;

        default:
            // Any other error happened.
            toast.error(t("Toasts.errors.generic"));
            break;
    }

    return apiError;
}
