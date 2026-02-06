<template>
    <ContentDialog
        v-model="visible"
        :title="t('PreviewDialog.videoTitle')"
        :max-width="900"
        content-class="pa-0"
    >
        <div class="d-flex justify-center">
            <video v-if="visible && src" :src="src" controls autoplay class="video-player">
                {{ t("PreviewDialog.videoNotSupported") }}
            </video>
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
.video-player {
    max-width: 100%;
    max-height: 70vh;
}
</style>
