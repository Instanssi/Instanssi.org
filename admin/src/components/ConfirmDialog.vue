<template>
    <BaseInfoDialog
        ref="dialog"
        :title="t('ConfirmDialog.title')"
        :width="500"
        :ok-text="t('ConfirmDialog.title')"
        ok-icon="fas fa-check"
    >
        {{ body }}
    </BaseInfoDialog>
</template>

<script setup lang="ts">
import { type Ref, ref } from "vue";
import { useI18n } from "vue-i18n";

import BaseInfoDialog from "@/components/BaseInfoDialog.vue";

const dialog: Ref<InstanceType<typeof BaseInfoDialog> | undefined> = ref(undefined);
const { t } = useI18n();
const body = ref("");

async function confirm(text: string): Promise<boolean> {
    body.value = text;
    const ok = await dialog.value?.modal();
    return ok ?? false;
}

defineExpose({ confirm });
</script>

<style scoped lang="scss"></style>
