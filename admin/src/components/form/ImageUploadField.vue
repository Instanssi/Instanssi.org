<template>
    <v-file-input
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
            <FontAwesomeIcon :icon="faImage" class="mr-2" />
        </template>
        <template v-if="previewUrl" #append-inner>
            <div
                class="image-preview"
                role="button"
                tabindex="0"
                :title="t('ImageUploadField.clickToPreview')"
                @click.stop="showPreview = true"
                @keydown.enter="showPreview = true"
                @keydown.space.prevent="showPreview = true"
            >
                <v-img :src="previewUrl" width="32" height="32" cover class="rounded" />
            </div>
        </template>
    </v-file-input>

    <ImagePreviewDialog v-model="showPreview" :src="previewUrl" />
</template>

<script setup lang="ts">
import { faImage } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import ImagePreviewDialog from "@/components/dialogs/ImagePreviewDialog.vue";
import { type FileValue, getFile } from "@/utils/file";

const props = withDefaults(
    defineProps<{
        modelValue: FileValue;
        currentImageUrl?: string | null;
        label: string;
        errorMessage?: string;
        accept?: string;
        required?: boolean;
    }>(),
    {
        currentImageUrl: null,
        errorMessage: undefined,
        accept: "image/*",
        required: false,
    }
);

const emit = defineEmits<{
    "update:modelValue": [value: FileValue];
}>();

const { t } = useI18n();
const showPreview = ref(false);
const objectUrl = ref<string | null>(null);
const wasCleared = ref(false);

const computedLabel = computed(() => {
    return props.required ? `${props.label} *` : props.label;
});

// Get the currently selected file
const selectedFile = computed(() => getFile(props.modelValue));

// Extract filename from URL
function getFilenameFromUrl(url: string | null): string | null {
    if (!url) return null;
    try {
        const pathname = new URL(url).pathname;
        return pathname.split("/").pop() || null;
    } catch {
        return url.split("/").pop()?.split("?")[0] || null;
    }
}

// Create a display value that shows the current URL filename when no new file is selected
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
    if (props.currentImageUrl) {
        const filename = getFilenameFromUrl(props.currentImageUrl);
        if (filename) {
            return new File([], filename);
        }
    }

    return null;
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
    return props.currentImageUrl ?? null;
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
.image-preview {
    cursor: pointer;
    border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    border-radius: 4px;
    padding: 1px;
    transition: border-color 0.2s;
}

.image-preview:hover {
    border-color: rgb(var(--v-theme-primary));
}

.image-preview:focus {
    outline: 2px solid rgb(var(--v-theme-primary));
    outline-offset: 1px;
}
</style>
