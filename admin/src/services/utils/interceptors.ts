import type { AxiosError } from "axios";
import { useToast } from "vue-toastification";
import { i18n } from "@/i18n";

export function errorResponseInterceptor(error: AxiosError) {
    const status = error.response?.status ?? 0;
    const path = error.response?.config.url ?? "";

    // Don't worry about this path -- we handle its errors in auth service.
    if (path.endsWith("/user_info/")) {
        return Promise.reject(error);
    }

    // If we receive 401 (not logged in), redirect user to login page.
    const toast = useToast();
    const { t } = i18n.global;
    if (status === 401) {
        toast.error(t("Toasts.errors.sessionTimedOut"));
        return Promise.reject(error);
    }

    // These are application errors, they should be handled in the requester functions.
    if (status >= 300 && status < 500 && status != 418) {
        return Promise.reject(error);
    }

    // This happens if axios timeouts
    if (error.code === "ECONNABORTED") {
        toast.error(t("Toasts.errors.timeout"));
        return Promise.reject(error);
    }

    switch (status) {
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
