import { ref, type Ref } from "vue";
import { useToast } from "vue-toastification";

export interface AsyncActionOptions {
    /** Toast message shown on success */
    successMessage: string;
    /** Toast message shown on failure */
    failureMessage: string;
}

export interface AsyncActionReturn {
    loading: Ref<boolean>;
    run: (fn: () => Promise<void> | void) => Promise<void>;
}

/**
 * Composable for async operations with loading state, success/error toasts, and error logging.
 */
export function useAsyncAction(options: AsyncActionOptions): AsyncActionReturn {
    const toast = useToast();
    const loading = ref(false);

    async function run(fn: () => Promise<void> | void): Promise<void> {
        loading.value = true;
        try {
            await fn();
            toast.success(options.successMessage);
        } catch (e) {
            toast.error(options.failureMessage);
            console.error(e);
        } finally {
            loading.value = false;
        }
    }

    return { loading, run };
}
