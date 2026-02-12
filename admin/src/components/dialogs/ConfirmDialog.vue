<template>
    <BaseInfoDialog
        ref="dialog"
        :title="t('General.confirm')"
        :width="500"
        :ok-text="t('General.confirm')"
        :loading="loading"
        :ok-icon="faCheck"
    >
        {{ body }}
    </BaseInfoDialog>
</template>

<script setup lang="ts">
import { faCheck } from "@fortawesome/free-solid-svg-icons";
import { type Ref, ref } from "vue";
import { useI18n } from "vue-i18n";

import BaseInfoDialog from "@/components/dialogs/BaseInfoDialog.vue";

type ConfirmedCallback = () => Promise<void>;

const dialog: Ref<InstanceType<typeof BaseInfoDialog> | undefined> = ref(undefined);
const { t } = useI18n();
const loading = ref(false);
const body = ref("");

async function confirm(text: string): Promise<boolean> {
    body.value = text;
    const ok = await dialog.value?.modal();
    return ok ?? false;
}

async function ifConfirmed(text: string, callback: ConfirmedCallback): Promise<void> {
    const ok = await confirm(text);
    if (ok) {
        loading.value = true;
        await callback();
        loading.value = false;
    }
}

defineExpose({ confirm, ifConfirmed });
</script>

<style scoped lang="scss"></style>
