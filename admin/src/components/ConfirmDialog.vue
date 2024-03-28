<template>
    <BaseDialog
        :title="t('ConfirmDialog.title')"
        :width="500"
        :ok-text="t('ConfirmDialog.title')"
        ok-icon="fas fa-check"
        ref="dialog"
    >
        {{ body }}
    </BaseDialog>
</template>

<script setup lang="ts">
import BaseDialog from "@/components/BaseDialog.vue";
import { type Ref, ref } from "vue";
import { useI18n } from "vue-i18n";

const dialog: Ref<InstanceType<typeof BaseDialog> | undefined> = ref(undefined);
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
