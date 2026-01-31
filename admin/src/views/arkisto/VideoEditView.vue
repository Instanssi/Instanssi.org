<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <v-card>
                <v-card-text>
                    <v-form @submit.prevent="submit">
                        <FormSection>
                            {{ t("VideoEditView.sections.basicInfo") }}
                        </FormSection>
                        <v-select
                            v-model.number="category.value.value"
                            :error-messages="category.errorMessage.value"
                            :items="categoryOptions"
                            variant="outlined"
                            :label="t('VideoEditView.labels.category') + ' *'"
                        />
                        <v-text-field
                            v-model="name.value.value"
                            :error-messages="name.errorMessage.value"
                            variant="outlined"
                            :label="t('VideoEditView.labels.name') + ' *'"
                        />
                        <VuetifyTiptap v-model="description.value.value" />
                        <div
                            v-if="description.errorMessage.value"
                            class="text-error text-caption mb-4"
                        >
                            {{ description.errorMessage.value }}
                        </div>

                        <FormSection>
                            {{ t("VideoEditView.sections.youtube") }}
                        </FormSection>
                        <v-text-field
                            v-model="youtubeUrl"
                            variant="outlined"
                            :label="t('VideoEditView.labels.youtubeUrl')"
                            :hint="t('VideoEditView.labels.youtubeUrlHint')"
                            persistent-hint
                            class="mb-4"
                        />
                        <v-text-field
                            v-model.number="youtubeStart.value.value"
                            :error-messages="youtubeStart.errorMessage.value"
                            variant="outlined"
                            :label="t('VideoEditView.labels.youtubeStart')"
                            type="number"
                            min="0"
                        />
                    </v-form>
                </v-card-text>
                <v-card-actions class="justify-end">
                    <v-btn variant="text" @click="goBack">
                        {{ t("General.cancel") }}
                    </v-btn>
                    <v-btn
                        variant="elevated"
                        color="primary"
                        :loading="saving"
                        :disabled="!meta.valid"
                        @click="submit"
                    >
                        <template #prepend>
                            <FontAwesomeIcon :icon="faSave" />
                        </template>
                        {{ t("General.save") }}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { faFloppyDisk as faSave } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { parseInt } from "lodash-es";
import { type GenericObject, useField, useForm } from "vee-validate";
import { type Ref, computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { number as yupNumber, object as yupObject, string as yupString } from "yup";

import * as api from "@/api";
import type { OtherVideoCategory } from "@/api";
import FormSection from "@/components/form/FormSection.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { useEvents } from "@/services/events";
import { handleApiError } from "@/utils/http";

const props = defineProps<{
    eventId: string;
    id?: string;
}>();

const { t } = useI18n();
const router = useRouter();
const toast = useToast();
const { getEventById } = useEvents();

const loading = ref(false);
const saving = ref(false);
const videoName = ref<string>("");
const eventId = computed(() => parseInt(props.eventId, 10));
const isEditMode = computed(() => props.id !== undefined);
const categories: Ref<OtherVideoCategory[]> = ref([]);
const youtubeUrl = ref<string>("");

const categoryOptions = computed(() =>
    categories.value.map((c) => ({ title: c.name, value: c.id }))
);

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = [
        {
            title: getEventById(eventId.value)?.name ?? "...",
            to: { name: "dashboard", params: { eventId: props.eventId } },
        },
        {
            title: t("VideosView.title"),
            to: { name: "arkisto-videos", params: { eventId: props.eventId } },
        },
    ];
    if (isEditMode.value) {
        items.push({ title: videoName.value || "...", disabled: true });
    } else {
        items.push({ title: t("Breadcrumbs.newVideo"), disabled: true });
    }
    return items;
});

// Form validation
const validationSchema = yupObject({
    category: yupNumber().required().min(1),
    name: yupString().required().min(1).max(64),
    description: yupString(),
    youtubeVideoId: yupString(),
    youtubeStart: yupNumber().nullable().min(0),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        category: null as number | null,
        name: "",
        description: "",
        youtubeVideoId: "",
        youtubeStart: null as number | null,
    },
});

const category = useField<number | null>("category");
const name = useField<string>("name");
const description = useField<string>("description");
const youtubeVideoId = useField<string>("youtubeVideoId");
const youtubeStart = useField<number | null>("youtubeStart");

/**
 * Extract YouTube video ID from various URL formats
 */
function extractYoutubeVideoId(url: string): string | null {
    if (!url) return null;

    // Handle various YouTube URL formats
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})/,
        /^([a-zA-Z0-9_-]{11})$/, // Direct video ID
    ];

    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match && match[1]) {
            return match[1];
        }
    }
    return null;
}

/**
 * Build YouTube URL from video ID
 */
function buildYoutubeUrl(videoId: string | null): string {
    if (!videoId) return "";
    return `https://www.youtube.com/watch?v=${videoId}`;
}

// Update video ID when URL changes
watch(youtubeUrl, (newUrl) => {
    const videoId = extractYoutubeVideoId(newUrl);
    youtubeVideoId.value.value = videoId ?? "";
});

const submit = handleSubmit(async (values) => {
    saving.value = true;
    let ok: boolean;
    if (isEditMode.value) {
        ok = await editVideo(parseInt(props.id!, 10), values);
    } else {
        ok = await createVideo(values);
    }
    saving.value = false;
    if (ok) {
        goBack();
    }
});

function buildYoutubePayload(values: GenericObject) {
    if (!values.youtubeVideoId) {
        return null;
    }
    return {
        video_id: values.youtubeVideoId,
        start: values.youtubeStart ?? null,
    };
}

async function createVideo(values: GenericObject) {
    try {
        await api.adminEventArkistoVideosCreate({
            path: { event_pk: eventId.value },
            body: {
                category: values.category,
                name: values.name,
                description: values.description || "",
                youtube_url: buildYoutubePayload(values),
            },
        });
        toast.success(t("VideoEditView.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("VideoEditView.createFailure"));
    }
    return false;
}

async function editVideo(videoId: number, values: GenericObject) {
    try {
        await api.adminEventArkistoVideosPartialUpdate({
            path: { event_pk: eventId.value, id: videoId },
            body: {
                category: values.category,
                name: values.name,
                description: values.description || "",
                youtube_url: buildYoutubePayload(values),
            },
        });
        toast.success(t("VideoEditView.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("VideoEditView.editFailure"));
    }
    return false;
}

async function loadCategories() {
    try {
        const response = await api.adminEventArkistoVideoCategoriesList({
            path: { event_pk: eventId.value },
            query: { limit: 100 },
        });
        categories.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load categories:", e);
    }
}

function goBack() {
    router.push({ name: "arkisto-videos", params: { eventId: props.eventId } });
}

onMounted(async () => {
    await loadCategories();

    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminEventArkistoVideosRetrieve({
                path: { event_pk: eventId.value, id: parseInt(props.id!, 10) },
            });
            const video = response.data!;
            videoName.value = video.name;
            const videoId = video.youtube_url?.video_id ?? "";
            youtubeUrl.value = buildYoutubeUrl(videoId);
            setValues({
                category: video.category,
                name: video.name,
                description: video.description ?? "",
                youtubeVideoId: videoId,
                youtubeStart: video.youtube_url?.start ?? null,
            });
        } catch (e) {
            toast.error(t("VideoEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
