<template>
    <div v-if="url" class="media-cell">
        <!-- Image: thumbnail + preview dialog -->
        <template v-if="mediaType === 'image'">
            <div
                class="image-thumbnail"
                role="button"
                tabindex="0"
                :title="t('General.clickToPreview')"
                @click="showImagePreview = true"
                @keydown.enter="showImagePreview = true"
                @keydown.space.prevent="showImagePreview = true"
            >
                <v-img :src="url" :width="size" :height="size" cover class="rounded" />
            </div>

            <ImagePreviewDialog v-model="showImagePreview" :src="url" :download-url="url" />
        </template>

        <!-- Video: play icon button + player dialog -->
        <template v-else-if="mediaType === 'video'">
            <v-btn
                icon
                variant="text"
                size="small"
                :title="t('General.clickToPreview')"
                @click="showVideoPreview = true"
            >
                <FontAwesomeIcon :icon="faCirclePlay" size="lg" />
            </v-btn>

            <VideoPreviewDialog v-model="showVideoPreview" :src="url" :download-url="url" />
        </template>

        <!-- Audio: audio icon button + player dialog -->
        <template v-else-if="mediaType === 'audio'">
            <v-btn
                icon
                variant="text"
                size="small"
                :title="t('General.clickToPreview')"
                @click="showAudioPreview = true"
            >
                <FontAwesomeIcon :icon="faVolumeHigh" size="lg" />
            </v-btn>

            <AudioPreviewDialog v-model="showAudioPreview" :src="url" :download-url="url" />
        </template>

        <!-- Other: file icon button + preview dialog -->
        <template v-else>
            <v-btn
                icon
                variant="text"
                size="small"
                :title="t('General.clickToPreview')"
                @click="showFilePreview = true"
            >
                <FontAwesomeIcon :icon="fileIcon" size="lg" />
            </v-btn>

            <FilePreviewDialog
                v-model="showFilePreview"
                :download-url="url"
                :filename="displayFilename"
            />
        </template>
    </div>
    <span v-else>{{ fallback }}</span>
</template>

<script setup lang="ts">
import { faCirclePlay, faVolumeHigh } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";

import AudioPreviewDialog from "@/components/dialogs/AudioPreviewDialog.vue";
import FilePreviewDialog from "@/components/dialogs/FilePreviewDialog.vue";
import ImagePreviewDialog from "@/components/dialogs/ImagePreviewDialog.vue";
import VideoPreviewDialog from "@/components/dialogs/VideoPreviewDialog.vue";
import { detectMediaType, getFileIcon, getFilenameFromUrl } from "@/utils/media";

const props = withDefaults(
    defineProps<{
        url: string | null;
        filename?: string | null;
        size?: number;
        fallback?: string;
    }>(),
    {
        filename: null,
        size: 40,
        fallback: "-",
    }
);

const { t } = useI18n();
const showImagePreview = ref(false);
const showVideoPreview = ref(false);
const showAudioPreview = ref(false);
const showFilePreview = ref(false);

const mediaType = computed(() => detectMediaType(props.url));
const fileIcon = computed(() => getFileIcon(props.url));

const displayFilename = computed(() => {
    if (props.filename) return props.filename;
    return getFilenameFromUrl(props.url) || props.url || "";
});
</script>

<style scoped>
.media-cell {
    display: inline-flex;
    align-items: center;
    vertical-align: middle;
    gap: 8px;
}

.image-thumbnail {
    cursor: pointer;
    border-radius: 4px;
    transition: opacity 0.2s;
    flex-shrink: 0;
}

.image-thumbnail:hover {
    opacity: 0.8;
}

.image-thumbnail:focus {
    outline: 2px solid rgb(var(--v-theme-primary));
    outline-offset: 1px;
}
</style>
