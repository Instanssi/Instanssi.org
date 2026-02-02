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
                        <v-textarea
                            v-model="description.value.value"
                            :error-messages="description.errorMessage.value"
                            variant="outlined"
                            :label="t('VideoEditView.labels.description')"
                            rows="4"
                        />

                        <FormSection>
                            {{ t("VideoEditView.sections.youtube") }}
                        </FormSection>
                        <v-text-field
                            v-model="youtubeUrl.value.value"
                            :error-messages="youtubeUrl.errorMessage.value"
                            variant="outlined"
                            :label="t('VideoEditView.labels.youtubeUrl') + ' *'"
                            :hint="t('VideoEditView.labels.youtubeUrlHint')"
                            persistent-hint
                            class="mb-4"
                        />
                    </v-form>
                </v-card-text>
                <v-card-actions class="justify-end">
                    <AuditLogButton
                        v-if="isEditMode"
                        app-label="arkisto"
                        model="othervideo"
                        :object-pk="props.id"
                    />
                    <v-spacer />
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
import { type Ref, computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { number as yupNumber, object as yupObject, string as yupString } from "yup";

import * as api from "@/api";
import type { OtherVideoCategory } from "@/api";
import AuditLogButton from "@/components/auditlog/AuditLogButton.vue";
import FormSection from "@/components/form/FormSection.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { useEvents } from "@/services/events";
import { handleApiError, type FieldMapping } from "@/utils/http";

/** Maps API field names (snake_case) to form field names (camelCase) */
const API_FIELD_MAPPING: FieldMapping = {
    category: "category",
    name: "name",
    description: "description",
    youtube_url: "youtubeUrl",
};

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

/**
 * Check if value looks like a YouTube URL or video ID
 */
function isValidYoutubeInput(value: string): boolean {
    if (!value) return false;
    // Accept YouTube URLs or direct 11-char video IDs
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)[a-zA-Z0-9_-]{11}/,
        /^[a-zA-Z0-9_-]{11}$/,
    ];
    return patterns.some((pattern) => pattern.test(value));
}

// Form validation
const validationSchema = yupObject({
    category: yupNumber().required().min(1),
    name: yupString().required().min(1).max(64),
    description: yupString(),
    youtubeUrl: yupString()
        .required()
        .test("youtube-url", "Invalid YouTube URL or video ID", (value) =>
            isValidYoutubeInput(value ?? "")
        ),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        category: null as number | null,
        name: "",
        description: "",
        youtubeUrl: "",
    },
});

const category = useField<number | null>("category");
const name = useField<string>("name");
const description = useField<string>("description");
const youtubeUrl = useField<string>("youtubeUrl");

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

function buildBody(values: GenericObject) {
    return {
        category: values.category,
        name: values.name,
        description: values.description || "",
        youtube_url: values.youtubeUrl,
    };
}

async function createVideo(values: GenericObject) {
    try {
        await api.adminEventArkistoVideosCreate({
            path: { event_pk: eventId.value },
            body: buildBody(values),
        });
        toast.success(t("VideoEditView.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("VideoEditView.createFailure"), API_FIELD_MAPPING);
    }
    return false;
}

async function editVideo(videoId: number, values: GenericObject) {
    try {
        await api.adminEventArkistoVideosPartialUpdate({
            path: { event_pk: eventId.value, id: videoId },
            body: buildBody(values),
        });
        toast.success(t("VideoEditView.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("VideoEditView.editFailure"), API_FIELD_MAPPING);
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
            setValues({
                category: video.category,
                name: video.name,
                description: video.description ?? "",
                youtubeUrl: video.youtube_url ?? "",
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
