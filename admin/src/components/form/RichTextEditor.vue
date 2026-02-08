<template>
    <div>
        <VuetifyTiptap
            v-if="!htmlMode"
            :model-value="modelValue"
            :extensions="imageExtensions"
            @update:model-value="emit('update:modelValue', $event as string)"
        />
        <v-textarea
            v-else
            :model-value="modelValue"
            variant="outlined"
            rows="12"
            auto-grow
            @update:model-value="emit('update:modelValue', $event)"
        />
        <v-btn variant="text" size="small" class="mt-1" @click="htmlMode = !htmlMode">
            <template #prepend>
                <FontAwesomeIcon :icon="htmlMode ? faEye : faCode" />
            </template>
            {{ htmlMode ? t("RichTextEditor.switchToVisual") : t("RichTextEditor.switchToHtml") }}
        </v-btn>
    </div>
</template>

<script setup lang="ts">
import { faCode, faEye } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import { Image } from "vuetify-pro-tiptap";

import * as api from "@/api";

const props = defineProps<{
    modelValue: string;
    eventId: number;
}>();

const emit = defineEmits<{
    "update:modelValue": [value: string];
}>();

const { t } = useI18n();
const toast = useToast();
const htmlMode = ref(false);

const imageExtensions = computed(() => [
    Image.configure({
        upload: async (file: File): Promise<string> => {
            try {
                const response = await api.adminEventUploadsFilesCreate({
                    path: { event_pk: props.eventId },
                    body: { file },
                });
                return response.data!.file_url!;
            } catch (e) {
                toast.error(t("RichTextEditor.uploadFailure"));
                console.error(e);
                throw e;
            }
        },
    }),
]);
</script>
