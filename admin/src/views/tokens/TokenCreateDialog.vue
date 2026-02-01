<template>
    <BaseInfoDialog
        ref="dialog"
        :title="t('TokenCreateDialog.title')"
        :width="500"
        :ok-text="t('TokenCreateDialog.create')"
        :ok-icon="faKey"
        :loading="saving"
    >
        <v-form @submit.prevent="submit">
            <v-text-field
                v-model="expiryString"
                type="datetime-local"
                variant="outlined"
                :label="t('TokenCreateDialog.labels.expiry')"
                :min="minDateString"
                :error-messages="expiryError"
            />
            <p class="text-caption mt-2 text-medium-emphasis">
                {{ t("TokenCreateDialog.expiryHint") }}
            </p>
        </v-form>
    </BaseInfoDialog>
</template>

<script setup lang="ts">
import { faKey } from "@fortawesome/free-solid-svg-icons";
import { type Ref, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";

import * as api from "@/api";
import BaseInfoDialog from "@/components/dialogs/BaseInfoDialog.vue";
import { handleApiError, type FieldMapping } from "@/utils/http";

const props = defineProps<{
    visible: boolean;
}>();

const emit = defineEmits<{
    "update:visible": [value: boolean];
    created: [token: string];
}>();

const { t } = useI18n();
const toast = useToast();

const dialog: Ref<InstanceType<typeof BaseInfoDialog> | undefined> = ref(undefined);
const saving = ref(false);
const expiryString = ref("");
const minDateString = ref("");
const expiryError = ref("");

/** Maps API field names to local field error refs */
const fieldMapping: FieldMapping = { expiry: "expiry" };

function setErrors(errors: Record<string, string>) {
    expiryError.value = errors.expiry ?? "";
}

// Format date for datetime-local input (YYYY-MM-DDTHH:mm)
function formatDateTimeLocal(date: Date): string {
    const pad = (n: number) => n.toString().padStart(2, "0");
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

// Default expiry: 30 days from now
function getDefaultExpiry(): string {
    const date = new Date();
    date.setDate(date.getDate() + 30);
    return formatDateTimeLocal(date);
}

function resetForm() {
    minDateString.value = formatDateTimeLocal(new Date());
    expiryString.value = getDefaultExpiry();
    expiryError.value = "";
}

watch(
    () => props.visible,
    async (newVal) => {
        if (newVal) {
            // Initialize form state once when dialog opens
            resetForm();
            // Loop allows retrying on failure
            while (true) {
                const ok = await dialog.value?.modal();
                if (!ok) {
                    // User cancelled
                    break;
                }
                const success = await submit();
                if (success) {
                    break;
                }
                // On failure, loop continues and dialog reopens for retry
            }
            emit("update:visible", false);
        }
    }
);

async function submit(): Promise<boolean> {
    if (!expiryString.value) {
        toast.error(t("TokenCreateDialog.expiryRequired"));
        return false;
    }

    const expiry = new Date(expiryString.value);
    if (isNaN(expiry.getTime())) {
        toast.error(t("TokenCreateDialog.expiryRequired"));
        return false;
    }

    saving.value = true;
    try {
        const response = await api.userTokensCreateToken({
            body: {
                expiry: expiry.toISOString(),
            },
        });
        toast.success(t("TokenCreateDialog.createSuccess"));
        emit("created", response.data!.token);
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("TokenCreateDialog.createFailure"), fieldMapping);
        return false;
    } finally {
        saving.value = false;
    }
}
</script>
