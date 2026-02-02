<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <v-card>
                <v-card-text>
                    <v-form @submit.prevent="submit">
                        <v-text-field
                            v-model="name.value.value"
                            :error-messages="name.errorMessage.value"
                            variant="outlined"
                            :label="t('VideoCategoryEditView.labels.name') + ' *'"
                        />
                    </v-form>
                </v-card-text>
                <v-card-actions class="justify-end">
                    <AuditLogButton
                        v-if="isEditMode"
                        app-label="arkisto"
                        model="othervideocategory"
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
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { object as yupObject, string as yupString } from "yup";

import * as api from "@/api";
import AuditLogButton from "@/components/auditlog/AuditLogButton.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { useEvents } from "@/services/events";
import { handleApiError, type FieldMapping } from "@/utils/http";

/** Maps API field names (snake_case) to form field names (camelCase) */
const API_FIELD_MAPPING: FieldMapping = {
    name: "name",
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
const categoryName = ref<string>("");
const eventId = computed(() => parseInt(props.eventId, 10));
const isEditMode = computed(() => props.id !== undefined);

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = [
        {
            title: getEventById(eventId.value)?.name ?? "...",
            to: { name: "dashboard", params: { eventId: props.eventId } },
        },
        {
            title: t("VideoCategoriesView.title"),
            to: { name: "arkisto-categories", params: { eventId: props.eventId } },
        },
    ];
    if (isEditMode.value) {
        items.push({ title: categoryName.value || "...", disabled: true });
    } else {
        items.push({ title: t("Breadcrumbs.newVideoCategory"), disabled: true });
    }
    return items;
});

// Form validation
const validationSchema = yupObject({
    name: yupString().required().min(1).max(64),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        name: "",
    },
});

const name = useField<string>("name");

const submit = handleSubmit(async (values) => {
    saving.value = true;
    let ok: boolean;
    if (isEditMode.value) {
        ok = await editCategory(parseInt(props.id!, 10), values);
    } else {
        ok = await createCategory(values);
    }
    saving.value = false;
    if (ok) {
        goBack();
    }
});

function buildBody(values: GenericObject) {
    return {
        name: values.name,
    };
}

async function createCategory(values: GenericObject) {
    try {
        await api.adminEventArkistoVideoCategoriesCreate({
            path: { event_pk: eventId.value },
            body: buildBody(values),
        });
        toast.success(t("VideoCategoryEditView.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(
            e,
            setErrors,
            toast,
            t("VideoCategoryEditView.createFailure"),
            API_FIELD_MAPPING
        );
    }
    return false;
}

async function editCategory(categoryId: number, values: GenericObject) {
    try {
        await api.adminEventArkistoVideoCategoriesPartialUpdate({
            path: { event_pk: eventId.value, id: categoryId },
            body: buildBody(values),
        });
        toast.success(t("VideoCategoryEditView.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(
            e,
            setErrors,
            toast,
            t("VideoCategoryEditView.editFailure"),
            API_FIELD_MAPPING
        );
    }
    return false;
}

function goBack() {
    router.push({ name: "arkisto-categories", params: { eventId: props.eventId } });
}

onMounted(async () => {
    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminEventArkistoVideoCategoriesRetrieve({
                path: { event_pk: eventId.value, id: parseInt(props.id!, 10) },
            });
            const category = response.data!;
            categoryName.value = category.name;
            setValues({
                name: category.name,
            });
        } catch (e) {
            toast.error(t("VideoCategoryEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
