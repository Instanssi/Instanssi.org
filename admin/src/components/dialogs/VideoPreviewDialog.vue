<template>
    <ContentDialog
        v-model="visible"
        :title="t('PreviewDialog.videoTitle')"
        :max-width="900"
        content-class="pa-0"
    >
        <template v-if="downloadUrl" #title-actions>
            <v-btn
                :href="downloadUrl"
                target="_blank"
                rel="noopener"
                variant="text"
                size="small"
                color="primary"
                tag="a"
            >
                <FontAwesomeIcon :icon="faDownload" class="mr-1" />
                {{ t("PreviewDialog.download") }}
            </v-btn>
        </template>
        <div class="d-flex justify-center">
            <video v-if="visible && src" :src="src" controls autoplay class="video-player">
                {{ t("PreviewDialog.videoNotSupported") }}
            </video>
        </div>
    </ContentDialog>
</template>

<script setup lang="ts">
import { faDownload } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { useI18n } from "vue-i18n";

import ContentDialog from "@/components/dialogs/ContentDialog.vue";

withDefaults(
    defineProps<{
        src: string | null | undefined;
        downloadUrl?: string | null;
    }>(),
    {
        downloadUrl: null,
    }
);

const { t } = useI18n();
const visible = defineModel<boolean>({ default: false });
</script>

<style scoped>
.video-player {
    max-width: 100%;
    max-height: 70vh;
}
</style>
