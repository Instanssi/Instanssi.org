<template>
    <BaseDialog
        ref="baseDialog"
        :title="title"
        :width="width"
        @open="emit('open')"
        @close="emit('close')"
    >
        <v-card-text>
            <slot name="default" />
        </v-card-text>
        <v-card-actions class="justify-end">
            <slot name="buttons">
                <v-btn variant="text" :prepend-icon="cancelIcon" @click="setResult(false)">
                    {{ cancelText ?? t("General.cancel") }}
                </v-btn>
                <v-btn
                    variant="elevated"
                    color="primary"
                    @click="setResult(true)"
                >
                    <template #prepend>
                        <FontAwesomeIcon v-if="loading" icon="spinner" spin />
                        <v-icon v-else :icon="okIcon" />
                    </template>
                    {{ okText ?? t("General.ok") }}
                </v-btn>
            </slot>
        </v-card-actions>
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
}>();
withDefaults(defineProps<Props>(), {
    width: 600,
    okText: undefined,
    okIcon: undefined,
    cancelText: undefined,
    cancelIcon: undefined,
    loading: undefined,
});
const setResult = (v: boolean) => baseDialog.value?.setResult(v);
const modal = () => baseDialog.value?.modal();
defineExpose({ modal, setResult });
</script>
