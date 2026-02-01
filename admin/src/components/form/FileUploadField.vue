<template>
    <v-file-input
        ref="fileInputRef"
        :model-value="displayValue"
        :label="computedLabel"
        :error-messages="errorMessage"
        :accept="accept"
        variant="outlined"
        prepend-icon=""
        clearable
        @update:model-value="handleFileChange"
        @click:clear="handleClear"
    >
        <template #prepend-inner>
            <FontAwesomeIcon :icon="faUpload" class="mr-2" />
        </template>
        <template v-if="previewUrl" #append-inner>
            <!-- Image preview -->
            <div
                v-if="fileType === 'image'"
                class="file-preview"
                role="button"
                tabindex="0"
                :title="t('FileUploadField.clickToPreview')"
                @click.stop="showImagePreview = true"
                @keydown.enter="showImagePreview = true"
                @keydown.space.prevent="showImagePreview = true"
            >
                <v-img :src="previewUrl" width="32" height="32" cover class="rounded" />
            </div>

            <!-- Video preview button -->
            <v-btn
                v-else-if="fileType === 'video'"
                icon
                variant="text"
                size="x-small"
                :title="t('FileUploadField.clickToPreview')"
                @click.stop="showVideoPreview = true"
            >
                <FontAwesomeIcon :icon="faCirclePlay" size="lg" />
            </v-btn>

            <!-- Audio preview button -->
            <v-btn
                v-else-if="fileType === 'audio'"
                icon
                variant="text"
                size="x-small"
                :title="t('FileUploadField.clickToPreview')"
                @click.stop="showAudioPreview = true"
            >
                <FontAwesomeIcon :icon="faVolumeHigh" size="lg" />
            </v-btn>

            <!-- Download button for other files -->
            <v-btn
                v-else
                icon
                variant="text"
                size="x-small"
                :href="previewUrl"
                target="_blank"
                :title="t('FileUploadField.download')"
                @click.stop
            >
                <FontAwesomeIcon :icon="faDownload" size="lg" />
            </v-btn>
        </template>
    </v-file-input>

    <!-- Image Preview Dialog -->
    <v-dialog v-model="showImagePreview" max-width="900">
        <v-card>
            <v-card-title class="d-flex justify-space-between align-center">
                <span>{{ t("FileUploadField.imagePreviewTitle") }}</span>
                <v-btn icon variant="text" density="compact" @click="showImagePreview = false">
                    <FontAwesomeIcon :icon="faXmark" />
                </v-btn>
            </v-card-title>
            <v-divider />
            <v-card-text class="d-flex justify-center pa-4">
                <v-img :src="previewUrl ?? undefined" max-height="70vh" max-width="100%" />
            </v-card-text>
        </v-card>
    </v-dialog>

    <!-- Video Preview Dialog -->
    <v-dialog v-model="showVideoPreview" max-width="900">
        <v-card>
            <v-card-title class="d-flex justify-space-between align-center">
                <span>{{ t("FileUploadField.videoPreviewTitle") }}</span>
                <v-btn icon variant="text" density="compact" @click="showVideoPreview = false">
                    <FontAwesomeIcon :icon="faXmark" />
                </v-btn>
            </v-card-title>
            <v-divider />
            <v-card-text class="d-flex justify-center pa-4">
                <video
                    v-if="showVideoPreview && previewUrl"
                    :src="previewUrl"
                    controls
                    autoplay
                    class="video-player"
                >
                    {{ t("FileUploadField.videoNotSupported") }}
                </video>
            </v-card-text>
        </v-card>
    </v-dialog>

    <!-- Audio Preview Dialog -->
    <v-dialog v-model="showAudioPreview" max-width="500">
        <v-card>
            <v-card-title class="d-flex justify-space-between align-center">
                <span>{{ t("FileUploadField.audioPreviewTitle") }}</span>
                <v-btn icon variant="text" density="compact" @click="showAudioPreview = false">
                    <FontAwesomeIcon :icon="faXmark" />
                </v-btn>
            </v-card-title>
            <v-divider />
            <v-card-text class="d-flex justify-center pa-4">
                <audio
                    v-if="showAudioPreview && previewUrl"
                    :src="previewUrl"
                    controls
                    autoplay
                    class="audio-player"
                >
                    {{ t("FileUploadField.audioNotSupported") }}
                </audio>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script setup lang="ts">
import {
    faCirclePlay,
    faDownload,
    faUpload,
    faVolumeHigh,
    faXmark,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import { type FileValue, getFile } from "@/utils/file";

// File type detection based on extension or MIME type
const IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "ico"];
const VIDEO_EXTENSIONS = ["mp4", "mkv", "webm", "avi", "mov", "wmv", "flv", "ogv"];
const AUDIO_EXTENSIONS = ["mp3", "ogg", "opus", "aac", "wav", "flac", "m4a", "wma"];

type FileType = "image" | "video" | "audio" | "other";

function detectFileType(filename: string | null, mimeType: string | null): FileType {
    // Try MIME type first
    if (mimeType) {
        if (mimeType.startsWith("image/")) return "image";
        if (mimeType.startsWith("video/")) return "video";
        if (mimeType.startsWith("audio/")) return "audio";
    }

    // Fall back to extension
    if (filename) {
        const ext = filename.split(".").pop()?.toLowerCase();
        if (ext) {
            if (IMAGE_EXTENSIONS.includes(ext)) return "image";
            if (VIDEO_EXTENSIONS.includes(ext)) return "video";
            if (AUDIO_EXTENSIONS.includes(ext)) return "audio";
        }
    }

    return "other";
}

function getFilenameFromUrl(url: string | null): string | null {
    if (!url) return null;
    try {
        const pathname = new URL(url).pathname;
        return pathname.split("/").pop() || null;
    } catch {
        // If URL parsing fails, try to extract filename directly
        return url.split("/").pop()?.split("?")[0] || null;
    }
}

const props = withDefaults(
    defineProps<{
        modelValue: FileValue;
        currentFileUrl?: string | null;
        label: string;
        errorMessage?: string;
        accept?: string;
        required?: boolean;
    }>(),
    {
        currentFileUrl: null,
        errorMessage: undefined,
        accept: undefined,
        required: false,
    }
);

const emit = defineEmits<{
    "update:modelValue": [value: FileValue];
}>();

const { t } = useI18n();
const fileInputRef = ref();
const showImagePreview = ref(false);
const showVideoPreview = ref(false);
const showAudioPreview = ref(false);
const objectUrl = ref<string | null>(null);
const wasCleared = ref(false);

const computedLabel = computed(() => {
    return props.required ? `${props.label} *` : props.label;
});

// Get the currently selected file
const selectedFile = computed(() => getFile(props.modelValue));

// Create a fake File object to display the current URL filename
const displayValue = computed((): FileValue => {
    // If user selected a new file, show that
    if (selectedFile.value) {
        return selectedFile.value;
    }

    // If cleared, show nothing
    if (wasCleared.value) {
        return null;
    }

    // If we have a current URL, create a placeholder to show the filename
    if (props.currentFileUrl) {
        const filename = getFilenameFromUrl(props.currentFileUrl);
        if (filename) {
            // Create a minimal File-like object for display purposes
            // VFileInput will show the filename from this
            return new File([], filename);
        }
    }

    return null;
});

// Determine file type from selected file or current URL
const fileType = computed<FileType>(() => {
    if (selectedFile.value) {
        return detectFileType(selectedFile.value.name, selectedFile.value.type);
    }
    if (!wasCleared.value && props.currentFileUrl) {
        const filename = getFilenameFromUrl(props.currentFileUrl);
        return detectFileType(filename, null);
    }
    return "other";
});

// Create object URL for selected file preview
watch(
    () => props.modelValue,
    (newValue) => {
        // Clean up previous object URL
        if (objectUrl.value) {
            URL.revokeObjectURL(objectUrl.value);
            objectUrl.value = null;
        }

        // Create new object URL for the selected file
        const file = getFile(newValue);
        if (file) {
            objectUrl.value = URL.createObjectURL(file);
            wasCleared.value = false;
        }
    },
    { immediate: true }
);

// Clean up object URL on unmount
onBeforeUnmount(() => {
    if (objectUrl.value) {
        URL.revokeObjectURL(objectUrl.value);
    }
});

// Preview URL: prefer newly selected file, fall back to existing server URL
const previewUrl = computed(() => {
    if (objectUrl.value) return objectUrl.value;
    if (wasCleared.value) return null;
    return props.currentFileUrl ?? null;
});

function handleFileChange(value: FileValue) {
    wasCleared.value = false;
    emit("update:modelValue", value);
}

function handleClear() {
    wasCleared.value = true;
    emit("update:modelValue", null);
}
</script>

<style scoped>
.file-preview {
    cursor: pointer;
    border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    border-radius: 4px;
    padding: 1px;
    transition: border-color 0.2s;
}

.file-preview:hover {
    border-color: rgb(var(--v-theme-primary));
}

.file-preview:focus {
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
</style>
