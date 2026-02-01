<template>
    <div v-if="url" class="media-cell">
        <!-- Image: thumbnail + preview dialog -->
        <template v-if="mediaType === 'image'">
            <div
                class="image-thumbnail"
                role="button"
                tabindex="0"
                :title="t('MediaCell.clickToPreview')"
                @click="showImagePreview = true"
                @keydown.enter="showImagePreview = true"
                @keydown.space.prevent="showImagePreview = true"
            >
                <v-img :src="url" :width="size" :height="size" cover class="rounded" />
            </div>

            <v-dialog v-model="showImagePreview" max-width="900">
                <v-card>
                    <v-card-title class="d-flex justify-space-between align-center">
                        <span>{{ t("MediaCell.imagePreviewTitle") }}</span>
                        <v-btn
                            icon
                            variant="text"
                            density="compact"
                            @click="showImagePreview = false"
                        >
                            <FontAwesomeIcon :icon="faXmark" />
                        </v-btn>
                    </v-card-title>
                    <v-divider />
                    <v-card-text class="d-flex justify-center pa-4">
                        <v-img :src="url" max-height="70vh" max-width="100%" />
                    </v-card-text>
                </v-card>
            </v-dialog>
        </template>

        <!-- Video: play icon button + player dialog -->
        <template v-else-if="mediaType === 'video'">
            <v-btn
                icon
                variant="text"
                size="small"
                :title="t('MediaCell.clickToPreview')"
                @click="showVideoPreview = true"
            >
                <FontAwesomeIcon :icon="faCirclePlay" size="lg" />
            </v-btn>

            <v-dialog v-model="showVideoPreview" max-width="900">
                <v-card>
                    <v-card-title class="d-flex justify-space-between align-center">
                        <span>{{ t("MediaCell.videoPreviewTitle") }}</span>
                        <v-btn
                            icon
                            variant="text"
                            density="compact"
                            @click="showVideoPreview = false"
                        >
                            <FontAwesomeIcon :icon="faXmark" />
                        </v-btn>
                    </v-card-title>
                    <v-divider />
                    <v-card-text class="d-flex justify-center pa-4">
                        <video
                            v-if="showVideoPreview"
                            :src="url"
                            controls
                            autoplay
                            class="video-player"
                        >
                            {{ t("MediaCell.videoNotSupported") }}
                        </video>
                    </v-card-text>
                </v-card>
            </v-dialog>
        </template>

        <!-- Audio: audio icon button + player dialog -->
        <template v-else-if="mediaType === 'audio'">
            <v-btn
                icon
                variant="text"
                size="small"
                :title="t('MediaCell.clickToPreview')"
                @click="showAudioPreview = true"
            >
                <FontAwesomeIcon :icon="faVolumeHigh" size="lg" />
            </v-btn>

            <v-dialog v-model="showAudioPreview" max-width="500">
                <v-card>
                    <v-card-title class="d-flex justify-space-between align-center">
                        <span>{{ t("MediaCell.audioPreviewTitle") }}</span>
                        <v-btn
                            icon
                            variant="text"
                            density="compact"
                            @click="showAudioPreview = false"
                        >
                            <FontAwesomeIcon :icon="faXmark" />
                        </v-btn>
                    </v-card-title>
                    <v-divider />
                    <v-card-text class="d-flex justify-center pa-4">
                        <audio
                            v-if="showAudioPreview"
                            :src="url"
                            controls
                            autoplay
                            class="audio-player"
                        >
                            {{ t("MediaCell.audioNotSupported") }}
                        </audio>
                    </v-card-text>
                </v-card>
            </v-dialog>
        </template>

        <!-- Other: just download icon -->
        <template v-else>
            <FontAwesomeIcon :icon="faDownload" class="other-icon ma-3" />
        </template>

        <!-- Always show filename as download link -->
        <a :href="url" target="_blank" class="filename-link" :title="t('MediaCell.download')">
            {{ displayFilename }}
        </a>
    </div>
    <span v-else>{{ fallback }}</span>
</template>

<script setup lang="ts">
import { faCirclePlay, faDownload, faVolumeHigh, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";

import { detectMediaType, getFilenameFromUrl } from "@/utils/media";

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

const mediaType = computed(() => detectMediaType(props.url));

const displayFilename = computed(() => {
    if (props.filename) return props.filename;
    return getFilenameFromUrl(props.url) || props.url || "";
});
</script>

<style scoped>
.media-cell {
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.image-thumbnail {
    cursor: pointer;
    border-radius: 4px;
    transition: opacity 0.2s;
    flex-shrink: 0;
    margin-top: 1px;
    margin-bottom: 3px;
}

.image-thumbnail:hover {
    opacity: 0.8;
}

.image-thumbnail:focus {
    outline: 2px solid rgb(var(--v-theme-primary));
    outline-offset: 1px;
}

.video-player {
    max-width: 100%;
    max-height: 70vh;
}

.audio-player {
    width: 100%;
    min-width: 300px;
}

.filename-link {
    word-break: break-all;
}

.other-icon {
    opacity: 0.7;
}
</style>
