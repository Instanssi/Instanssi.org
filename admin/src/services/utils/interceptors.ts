import type { AxiosError } from "axios";
import { useToast } from "vue-toastification";

import { i18n } from "@/i18n";

export function errorResponseInterceptor(error: AxiosError) {
    // Don't worry about this path -- we handle its errors in auth service.
    const path = error.response?.config.url ?? "";
    if (path.endsWith("/user_info/")) {
        return Promise.reject(error);
    }

    // First, check if the error was due to timeout.
    const toast = useToast();
    const { t } = i18n.global;
    if (error.code === "ECONNABORTED") {
        toast.error(t("Toasts.errors.timeout"));
        return Promise.reject(error);
    }

    // Then, see if it was server side error code.
    const status = error.response?.status ?? 0;
    switch (status) {
        case 400:
            // Validation errors - let the caller handle these via handleApiError
            break;

        case 401:
            toast.error(t("Toasts.errors.sessionTimedOut"));
            break;

        case 409:
            toast.error(t("Toasts.errors.conflict"));
            break;

        case 418:
            // Mostly for testing :)
            toast.warning(t("Toasts.errors.teapot"));
            break;

        case 500:
            // Something is badly wrong server-side
            toast.error(t("Toasts.errors.ise"));
            break;

        case 502:
        case 503:
        case 504:
            // These usually happen if server is down for maintenance etc.
            toast.error(t("Toasts.errors.gateway"));
            break;

        default:
            // Any other error happened.
            toast.error(t("Toasts.errors.generic"));
            break;
    }

    return Promise.reject(error);
}
