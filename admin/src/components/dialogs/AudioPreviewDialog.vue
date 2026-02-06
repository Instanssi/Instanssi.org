<template>
    <ContentDialog
        v-model="visible"
        :title="t('PreviewDialog.audioTitle')"
        :max-width="500"
        content-class="pa-0"
    >
        <div class="d-flex justify-center">
            <audio v-if="visible && src" :src="src" controls autoplay class="audio-player">
                {{ t("PreviewDialog.audioNotSupported") }}
            </audio>
        </div>
    </ContentDialog>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import ContentDialog from "@/components/dialogs/ContentDialog.vue";

defineProps<{
    src: string | null | undefined;
}>();

const { t } = useI18n();
const visible = defineModel<boolean>({ default: false });
</script>

<style scoped>
.audio-player {
    width: 100%;
    min-width: 300px;
}
</style>
