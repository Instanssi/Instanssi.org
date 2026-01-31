<template>
    <span v-if="videoId">
        <a href="#" @click.prevent="showDialog = true">{{ videoId }}</a>
        <span v-if="startTime"> @ {{ formattedTime }}</span>
        <a :href="value!" target="_blank" rel="noopener" class="external-link">
            <FontAwesomeIcon :icon="faExternalLinkAlt" />
        </a>

        <v-dialog v-model="showDialog" max-width="800">
            <v-card>
                <v-card-title class="d-flex justify-space-between align-center">
                    <span>{{ videoId }}</span>
                    <v-btn icon variant="text" @click="showDialog = false">
                        <FontAwesomeIcon :icon="faTimes" />
                    </v-btn>
                </v-card-title>
                <v-card-text class="pa-0">
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
                </v-card-text>
            </v-card>
        </v-dialog>
    </span>
    <span v-else>{{ fallback }}</span>
</template>

<script setup lang="ts">
/**
 * YoutubeCell - Display YouTube URLs in data tables
 * Shows video ID and start time (if present) as a clickable link.
 * Clicking opens a dialog with the embedded video.
 */
import { faExternalLinkAlt, faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, ref } from "vue";

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

const formattedTime = computed(() => {
    if (!startTime.value) return "";
    return formatTime(startTime.value);
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

.external-link {
    margin-left: 0.5em;
    opacity: 0.6;
    font-size: 0.85em;
}

.external-link:hover {
    opacity: 1;
}
</style>
