<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <v-card>
                <v-card-text>
                    <v-form @submit.prevent="submit">
                        <v-file-input
                            v-model="file.value.value"
                            :label="t('UploadEditView.labels.file') + (isEditMode ? '' : ' *')"
                            :error-messages="file.errorMessage.value"
                            variant="outlined"
                            prepend-icon=""
                            clearable
                        >
                            <template #prepend>
                                <FontAwesomeIcon :icon="faUpload" />
                            </template>
                        </v-file-input>
                        <v-alert
                            v-if="isEditMode && currentFileUrl"
                            type="info"
                            variant="tonal"
                            class="mb-4"
                        >
                            <div class="d-flex align-center">
                                <span class="mr-2">{{ t("UploadEditView.labels.fileUrl") }}:</span>
                                <a
                                    :href="currentFileUrl"
                                    target="_blank"
                                    class="text-decoration-none mr-2"
                                >
                                    {{ getFilename(currentFileUrl) }}
                                </a>
                                <v-btn
                                    icon
                                    variant="text"
                                    size="small"
                                    @click="copyUrl(currentFileUrl)"
                                >
                                    <FontAwesomeIcon :icon="faCopy" />
                                </v-btn>
                            </div>
                        </v-alert>
                        <v-textarea
                            v-model="description.value.value"
                            :error-messages="description.errorMessage.value"
                            variant="outlined"
                            :label="t('UploadEditView.labels.description')"
                            rows="3"
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
import { faCopy, faFloppyDisk as faSave, faUpload } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { parseInt } from "lodash-es";
import { type GenericObject, useField, useForm } from "vee-validate";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { mixed as yupMixed, object as yupObject, string as yupString } from "yup";

import * as api from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { useEvents } from "@/services/events";
import { type FileValue, getFile } from "@/utils/file";
import { toFormData } from "@/utils/formdata";
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
const itemDescription = ref<string>("");
const eventId = computed(() => parseInt(props.eventId, 10));
const isEditMode = computed(() => props.id !== undefined);
const currentFileUrl = ref<string | null>(null);

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = [
        {
            title: getEventById(eventId.value)?.name ?? "...",
            to: { name: "dashboard", params: { eventId: props.eventId } },
        },
        {
            title: t("UploadsView.title"),
            to: { name: "uploads", params: { eventId: props.eventId } },
        },
    ];
    if (isEditMode.value) {
        items.push({ title: itemDescription.value || "...", disabled: true });
    } else {
        items.push({ title: t("Breadcrumbs.newUpload"), disabled: true });
    }
    return items;
});

// Form validation
const validationSchema = yupObject({
    description: yupString().max(255),
    file: yupMixed()
        .nullable()
        .test("file-required", t("UploadEditView.fileRequired"), (value) => {
            // File is required for create mode only
            if (currentFileUrl.value) return true; // Existing file in edit mode
            return !!getFile(value as FileValue);
        }),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        description: "",
        file: null as FileValue,
    },
});

const description = useField<string>("description");
const file = useField<FileValue>("file");

function getFilename(url: string): string {
    try {
        const pathname = new URL(url).pathname;
        return pathname.split("/").pop() || url;
    } catch {
        return url;
    }
}

async function copyUrl(url: string): Promise<void> {
    try {
        await navigator.clipboard.writeText(url);
        toast.success(t("UploadsView.copySuccess"));
    } catch {
        toast.error(t("UploadsView.copyFailure"));
    }
}

const submit = handleSubmit(async (values) => {
    saving.value = true;
    let ok: boolean;
    if (isEditMode.value) {
        ok = await editItem(parseInt(props.id!, 10), values);
    } else {
        ok = await createItem(values);
    }
    saving.value = false;
    if (ok) {
        goBack();
    }
});

async function createItem(values: GenericObject) {
    const selectedFile = getFile(values.file);
    if (!selectedFile) {
        return false;
    }
    try {
        await api.adminEventUploadsFilesCreate({
            path: { event_pk: eventId.value },
            body: {
                description: values.description || undefined,
                file: selectedFile,
            },
            bodySerializer: toFormData,
        });
        toast.success(t("UploadEditView.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("UploadEditView.createFailure"), {
            description: "description",
            file: "file",
        });
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        await api.adminEventUploadsFilesPartialUpdate({
            path: { event_pk: eventId.value, id: itemId },
            body: {
                description: values.description || "",
            },
            bodySerializer: toFormData,
        });
        toast.success(t("UploadEditView.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("UploadEditView.editFailure"), {
            description: "description",
        });
    }
    return false;
}

function goBack() {
    router.push({ name: "uploads", params: { eventId: props.eventId } });
}

onMounted(async () => {
    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminEventUploadsFilesRetrieve({
                path: { event_pk: eventId.value, id: parseInt(props.id!, 10) },
            });
            const item = response.data!;
            itemDescription.value = item.description || getFilename(item.file);
            currentFileUrl.value = item.file;
            setValues({
                description: item.description ?? "",
            });
        } catch (e) {
            toast.error(t("UploadEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
