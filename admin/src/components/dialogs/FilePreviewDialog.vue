<template>
    <ContentDialog
        v-model="visible"
        :title="t('PreviewDialog.fileTitle')"
        :max-width="500"
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
        <div class="d-flex flex-column align-center justify-center pa-8">
            <FontAwesomeIcon :icon="fileIcon" size="6x" class="file-icon" />
            <span v-if="filename" class="mt-4 text-body-2">{{ filename }}</span>
        </div>
    </ContentDialog>
</template>

<script setup lang="ts">
import { faDownload } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import ContentDialog from "@/components/dialogs/ContentDialog.vue";
import { getFileIcon } from "@/utils/media";

const props = withDefaults(
    defineProps<{
        downloadUrl: string;
        filename?: string | null;
    }>(),
    {
        filename: null,
    }
);

const { t } = useI18n();
const visible = defineModel<boolean>({ default: false });
const fileIcon = computed(() => getFileIcon(props.downloadUrl));
</script>

<style scoped>
.file-icon {
    opacity: 0.4;
}
</style>
