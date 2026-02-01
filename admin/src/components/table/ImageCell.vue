<template>
    <div v-if="url" class="image-cell">
        <div
            class="image-thumbnail"
            role="button"
            tabindex="0"
            :title="t('ImageCell.clickToPreview')"
            @click="showPreview = true"
            @keydown.enter="showPreview = true"
            @keydown.space.prevent="showPreview = true"
        >
            <v-img :src="url" :width="size" :height="size" cover class="rounded pa-0 ma-0" />
        </div>

        <v-dialog v-model="showPreview" max-width="900">
            <v-card>
                <v-card-title class="d-flex justify-space-between align-center">
                    <span>{{ t("ImageCell.previewTitle") }}</span>
                    <v-btn icon variant="text" density="compact" @click="showPreview = false">
                        <FontAwesomeIcon :icon="faXmark" />
                    </v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text class="d-flex justify-center pa-4">
                    <v-img :src="url" max-height="70vh" max-width="100%" />
                </v-card-text>
            </v-card>
        </v-dialog>
    </div>
    <div v-else class="image-placeholder" :style="{ width: `${size}px`, height: `${size}px` }">
        <FontAwesomeIcon :icon="faImage" class="placeholder-icon" />
    </div>
</template>

<script setup lang="ts">
import { faImage, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { ref } from "vue";
import { useI18n } from "vue-i18n";

withDefaults(
    defineProps<{
        url: string | null;
        size?: number;
    }>(),
    {
        size: 40,
    }
);

const { t } = useI18n();
const showPreview = ref(false);
</script>

<style scoped>
.image-cell {
    align-items: center;
    margin-top: 3px;
    margin-bottom: 3px;
}

.image-thumbnail {
    cursor: pointer;
    border-radius: 4px;
    transition: opacity 0.2s;
    flex-shrink: 0;
    margin: 0;
}

.image-thumbnail:hover {
    opacity: 0.8;
}

.image-thumbnail:focus {
    outline: 2px solid rgb(var(--v-theme-primary));
    outline-offset: 1px;
}

.image-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px dashed rgba(var(--v-border-color), var(--v-border-opacity));
    border-radius: 4px;
    background-color: rgba(var(--v-theme-surface-variant), 0.3);
    margin-top: 3px;
    margin-bottom: 3px;
}

.placeholder-icon {
    opacity: 0.4;
    font-size: 1.2em;
}
</style>
