<template>
    <div>
        <v-select
            :model-value="modelValue"
            :items="items"
            :label="label"
            :placeholder="placeholder"
            :no-data-text="noDataText"
            :loading="loading"
            variant="outlined"
            density="compact"
            item-value="value"
            item-title="title"
            @update:model-value="emit('update:modelValue', $event)"
        >
            <template #item="{ item, props: itemProps }">
                <v-list-item v-bind="itemProps" :title="undefined">
                    <template #prepend>
                        <v-img
                            :src="item.raw.value ?? undefined"
                            :width="thumbnailSize"
                            :height="thumbnailSize"
                            cover
                            class="rounded mr-3"
                        >
                            <template #placeholder>
                                <div class="d-flex align-center justify-center fill-height">
                                    <v-progress-circular
                                        indeterminate
                                        size="20"
                                        width="2"
                                        color="grey"
                                    />
                                </div>
                            </template>
                            <template #error>
                                <div
                                    class="d-flex align-center justify-center fill-height bg-grey-lighten-3"
                                >
                                    <FontAwesomeIcon :icon="faImage" class="text-grey" />
                                </div>
                            </template>
                        </v-img>
                    </template>
                    <v-list-item-title>{{ item.raw.title }}</v-list-item-title>
                </v-list-item>
            </template>
            <template #selection="{ item }">
                <div class="d-flex align-center">
                    <v-img
                        :src="item.raw.value ?? undefined"
                        :width="thumbnailSize"
                        :height="thumbnailSize"
                        cover
                        class="rounded mr-2"
                    >
                        <template #error>
                            <div
                                class="d-flex align-center justify-center fill-height bg-grey-lighten-3"
                            >
                                <FontAwesomeIcon :icon="faImage" class="text-grey" />
                            </div>
                        </template>
                    </v-img>
                    <span>{{ item.raw.title }}</span>
                </div>
            </template>
        </v-select>

        <!-- Large preview of selected image -->
        <v-expand-transition>
            <div v-if="modelValue && showPreview" class="mt-2">
                <v-img
                    :src="modelValue"
                    :max-height="previewMaxHeight"
                    contain
                    class="rounded border"
                >
                    <template #placeholder>
                        <div class="d-flex align-center justify-center fill-height">
                            <v-progress-circular indeterminate color="primary" />
                        </div>
                    </template>
                    <template #error>
                        <div
                            class="d-flex align-center justify-center fill-height bg-grey-lighten-3"
                            style="min-height: 100px"
                        >
                            <FontAwesomeIcon :icon="faImage" size="2x" class="text-grey" />
                        </div>
                    </template>
                </v-img>
            </div>
        </v-expand-transition>
    </div>
</template>

<script setup lang="ts">
import { faImage } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

export interface ImageSelectItem {
    title: string;
    value: string | null;
}

withDefaults(
    defineProps<{
        modelValue: string | null;
        items: ImageSelectItem[];
        label?: string;
        placeholder?: string;
        noDataText?: string;
        loading?: boolean;
        showPreview?: boolean;
        thumbnailSize?: number;
        previewMaxHeight?: number;
    }>(),
    {
        label: undefined,
        placeholder: undefined,
        noDataText: undefined,
        loading: false,
        showPreview: true,
        thumbnailSize: 40,
        previewMaxHeight: 200,
    }
);

const emit = defineEmits<{
    "update:modelValue": [value: string | null];
}>();
</script>
