<template>
    <BaseDialog
        ref="baseDialog"
        :title="title"
        :width="width"
        @open="emit('open')"
        @close="emit('close')"
    >
        <v-form @submit.prevent="emit('submit')">
            <v-card-text>
                <slot name="default" />
            </v-card-text>
            <v-card-actions class="justify-end">
                <slot name="buttons">
                    <v-btn variant="text" :prepend-icon="cancelIcon" @click="setResult(false)">
                        {{ cancelText ?? t("General.cancel") }}
                    </v-btn>
                    <v-btn variant="elevated" color="primary" type="submit">
                        <template #prepend>
                            <FontAwesomeIcon v-if="loading" icon="spinner" spin />
                            <v-icon v-else :icon="okIcon" />
                        </template>
                        {{ okText ?? t("General.ok") }}
                    </v-btn>
                </slot>
            </v-card-actions>
        </v-form>
    </BaseDialog>
</template>

<script setup lang="ts">
import { type Ref, ref } from "vue";
import { useI18n } from "vue-i18n";

import BaseDialog from "@/components/BaseDialog.vue";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

const { t } = useI18n();
const baseDialog: Ref<InstanceType<typeof BaseDialog> | undefined> = ref();

interface Props {
    width?: number;
    title: string;
    cancelText?: string;
    cancelIcon?: string | undefined;
    okText?: string;
    okIcon?: string | undefined;
    loading?: boolean | undefined;
}
const emit = defineEmits<{
    open: [];
    close: [];
    submit: [];
}>();
withDefaults(defineProps<Props>(), {
    width: 600,
    okText: undefined,
    okIcon: undefined,
    cancelText: undefined,
    cancelIcon: undefined,
    loading: undefined,
});

function setResult(v: boolean): void {
    baseDialog.value?.setResult(v);
}

async function modal(): Promise<void> {
    await baseDialog.value?.modal();
}

defineExpose({ modal, setResult });
</script>
