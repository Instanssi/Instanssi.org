<template>
    <BaseInfoDialog
        ref="dialog"
        :title="t('TokenCreatedDialog.title')"
        :width="600"
        :ok-text="t('General.ok')"
        :ok-icon="faCheck"
        cancel-text=""
    >
        <v-alert type="warning" variant="tonal" class="mb-4">
            {{ t("TokenCreatedDialog.warning") }}
        </v-alert>

        <v-text-field
            :model-value="token"
            variant="outlined"
            readonly
            :label="t('TokenCreatedDialog.labels.token')"
            class="token-field"
        >
            <template #append-inner>
                <v-btn
                    variant="text"
                    size="small"
                    :title="t('TokenCreatedDialog.copyToClipboard')"
                    @click="copyToClipboard"
                >
                    <FontAwesomeIcon :icon="faCopy" />
                </v-btn>
            </template>
        </v-text-field>
    </BaseInfoDialog>
</template>

<script setup lang="ts">
import { faCheck, faCopy } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { type Ref, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";

import BaseInfoDialog from "@/components/dialogs/BaseInfoDialog.vue";

const props = defineProps<{
    visible: boolean;
    token: string;
}>();

const emit = defineEmits<{
    "update:visible": [value: boolean];
}>();

const { t } = useI18n();
const toast = useToast();

const dialog: Ref<InstanceType<typeof BaseInfoDialog> | undefined> = ref(undefined);

watch(
    () => props.visible,
    async (newVal) => {
        if (newVal) {
            await dialog.value?.modal();
            emit("update:visible", false);
        }
    }
);

async function copyToClipboard() {
    try {
        await navigator.clipboard.writeText(props.token);
        toast.success(t("TokenCreatedDialog.copySuccess"));
    } catch (e) {
        toast.error(t("TokenCreatedDialog.copyFailure"));
        console.error(e);
    }
}
</script>

<style scoped>
.token-field :deep(input) {
    font-family: monospace;
    font-size: 0.9em;
}
</style>
