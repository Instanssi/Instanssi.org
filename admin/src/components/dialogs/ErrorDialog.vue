<template>
    <BaseDialog ref="baseDialog" :title="title" :width="500">
        <template #title>
            <div class="justify-left text-error">
                <FontAwesomeIcon :icon="faTriangleExclamation" class="mr-2" />
                {{ title }}
            </div>
            <div class="justify-end">
                <v-btn density="compact" variant="text" @click="close">
                    <FontAwesomeIcon :icon="faXmark" />
                </v-btn>
            </div>
        </template>
        <v-card-text>
            <slot />
        </v-card-text>
        <v-card-actions class="justify-end">
            <v-btn variant="elevated" color="error" @click="close">
                {{ t("General.ok") }}
            </v-btn>
        </v-card-actions>
    </BaseDialog>
</template>

<script setup lang="ts">
import { faTriangleExclamation, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { type Ref, ref } from "vue";
import { useI18n } from "vue-i18n";

import BaseDialog from "@/components/dialogs/BaseDialog.vue";

defineProps<{
    title: string;
}>();

const { t } = useI18n();
const baseDialog: Ref<InstanceType<typeof BaseDialog> | undefined> = ref(undefined);

async function open(): Promise<void> {
    await baseDialog.value?.modal();
}

function close(): void {
    baseDialog.value?.setResult(true);
}

defineExpose({ open });
</script>
