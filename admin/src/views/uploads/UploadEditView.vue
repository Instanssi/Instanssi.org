<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <v-card>
                <v-card-text>
                    <v-form @submit.prevent="submit">
                        <FileUploadField
                            v-model="file.value.value"
                            :current-file-url="currentFileUrl"
                            :label="t('UploadEditView.labels.file')"
                            :error-message="file.errorMessage.value"
                            :required="!isEditMode"
                        />
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
                    <AuditLogButton
                        v-if="isEditMode"
                        app-label="admin_upload"
                        model="uploadedfile"
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
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { mixed as yupMixed, object as yupObject, string as yupString } from "yup";

import * as api from "@/api";
import AuditLogButton from "@/components/auditlog/AuditLogButton.vue";
import FileUploadField from "@/components/form/FileUploadField.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { useEvents } from "@/services/events";
import { type FileValue, getFile } from "@/utils/file";
import { prepareFileField, toFormData } from "@/utils/formdata";
import { handleApiError, type FieldMapping } from "@/utils/http";

/** Maps API field names (snake_case) to form field names (camelCase) */
const API_FIELD_MAPPING: FieldMapping = {
    description: "description",
    file: "file",
};

const props = defineProps<{
    eventId: string;
    id?: string;
}>();

const { t } = useI18n();
const route = useRoute();
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
        file: undefined as FileValue | undefined,
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

function buildBody(values: GenericObject, isCreate: boolean) {
    const fileGetter = isCreate ? getFile : prepareFileField;
    return {
        description: values.description || "",
        file: fileGetter(values.file),
    };
}

async function createItem(values: GenericObject) {
    const body = buildBody(values, true);
    if (!body.file) {
        return false;
    }
    try {
        await api.adminEventUploadsFilesCreate({
            path: { event_pk: eventId.value },
            body: body as typeof body & { file: File },
            bodySerializer: () => toFormData(body),
        });
        toast.success(t("UploadEditView.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("UploadEditView.createFailure"), API_FIELD_MAPPING);
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    const body = buildBody(values, false);
    try {
        await api.adminEventUploadsFilesPartialUpdate({
            path: { event_pk: eventId.value, id: itemId },
            // Type assertion needed: our bodySerializer handles null for file clearing
            body: body as api.PatchedUploadedFileRequest,
            bodySerializer: () => toFormData(body),
        });
        toast.success(t("UploadEditView.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("UploadEditView.editFailure"), API_FIELD_MAPPING);
    }
    return false;
}

function goBack() {
    router.push({ name: "uploads", params: { eventId: props.eventId }, query: route.query });
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
