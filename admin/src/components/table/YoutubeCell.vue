<template>
    <div v-if="videoId">
        <v-btn
            icon
            variant="text"
            size="small"
            :title="t('General.clickToPreview')"
            @click="showDialog = true"
        >
            <FontAwesomeIcon :icon="faYoutube" size="lg" />
        </v-btn>

        <ContentDialog
            v-model="showDialog"
            :title="dialogTitle"
            :max-width="800"
            content-class="pa-0"
        >
            <template #title-actions>
                <v-btn
                    :href="value ?? ''"
                    target="_blank"
                    rel="noopener"
                    variant="text"
                    size="small"
                    color="primary"
                    tag="a"
                >
                    <FontAwesomeIcon :icon="faYoutube" class="mr-1" />
                    YouTube
                </v-btn>
            </template>
            <div class="video-container">
                <iframe
                    v-if="showDialog"
                    :src="embedUrl"
                    frameborder="0"
                    allow="
                        accelerometer;
                        autoplay;
                        clipboard-write;
                        encrypted-media;
                        gyroscope;
                        picture-in-picture;
                    "
                    allowfullscreen
                />
            </div>
        </ContentDialog>
    </div>
    <span v-else>{{ fallback }}</span>
</template>

<script setup lang="ts">
/**
 * YoutubeCell - Display YouTube URLs in data tables
 * Shows a YouTube icon button that opens a dialog with the embedded video.
 */
import { faYoutube } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";

import ContentDialog from "@/components/dialogs/ContentDialog.vue";

const { t } = useI18n();
const showDialog = ref(false);

const props = withDefaults(
    defineProps<{
        value?: string | null;
        fallback?: string;
    }>(),
    {
        value: null,
        fallback: "-",
    }
);

/**
 * Parse YouTube URL and extract video ID and start time
 */
function parseYoutubeUrl(urlString: string): { videoId: string | null; startTime: number | null } {
    try {
        const url = new URL(urlString);
        const videoId = url.searchParams.get("v");
        const start = url.searchParams.get("start");
        return {
            videoId,
            startTime: start ? parseInt(start, 10) : null,
        };
    } catch {
        return { videoId: null, startTime: null };
    }
}

/**
 * Format seconds as human-readable time (e.g., "1:30" or "1:02:30")
 */
function formatTime(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    }
    return `${minutes}:${secs.toString().padStart(2, "0")}`;
}

const parsed = computed(() => {
    if (!props.value) return { videoId: null, startTime: null };
    return parseYoutubeUrl(props.value);
});

const videoId = computed(() => parsed.value.videoId);
const startTime = computed(() => parsed.value.startTime);

const dialogTitle = computed(() => {
    const base = t("YoutubeCell.dialogTitle");
    if (startTime.value) {
        return `${base} (@ ${formatTime(startTime.value)})`;
    }
    return base;
});

const embedUrl = computed(() => {
    if (!videoId.value) return "";
    let url = `https://www.youtube.com/embed/${videoId.value}`;
    if (startTime.value) {
        url += `?start=${startTime.value}`;
    }
    return url;
});
</script>

<style scoped>
.video-container {
    position: relative;
    padding-bottom: 56.25%; /* 16:9 aspect ratio */
    height: 0;
    overflow: hidden;
}

.video-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}
</style>
