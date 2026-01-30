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
                            :label="t('EventDialog.labels.name') + ' *'"
                        />
                        <v-text-field
                            v-model="tag.value.value"
                            :error-messages="tag.errorMessage.value"
                            variant="outlined"
                            :label="t('EventDialog.labels.tag') + ' *'"
                        />
                        <v-text-field
                            v-model="date.value.value"
                            type="date"
                            :error-messages="date.errorMessage.value"
                            variant="outlined"
                            :label="t('EventDialog.labels.date') + ' *'"
                        />
                        <v-text-field
                            v-model="mainurl.value.value"
                            :error-messages="mainurl.errorMessage.value"
                            variant="outlined"
                            :label="t('EventDialog.labels.mainUrl') + ' *'"
                        />
                        <v-switch
                            v-model="archived.value.value"
                            :error-messages="archived.errorMessage.value"
                            :label="archivedLabel"
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
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import {
    date as yupDate,
    boolean as yupBoolean,
    object as yupObject,
    string as yupString,
} from "yup";

import * as api from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/LayoutBase.vue";
import { useEvents } from "@/services/events";
import { handleApiError } from "@/utils/http";

const props = defineProps<{
    id?: string;
}>();

const { t } = useI18n();
const router = useRouter();
const toast = useToast();
const { getLatestEvent, refreshEvents } = useEvents();

const loading = ref(false);
const saving = ref(false);
const eventName = ref<string>("");
const isEditMode = computed(() => props.id !== undefined);

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const event = getLatestEvent();
    const items: BreadcrumbItem[] = [
        {
            title: event?.name ?? "...",
            to: event ? { name: "dashboard", params: { eventId: event.id } } : undefined,
        },
        { title: t("EventView.title"), to: { name: "events" } },
    ];
    if (isEditMode.value) {
        items.push({ title: eventName.value || "...", disabled: true });
    } else {
        items.push({ title: t("Breadcrumbs.newEvent"), disabled: true });
    }
    return items;
});

const archivedLabel = computed(() =>
    archived.value.value
        ? t("EventDialog.labels.isArchived")
        : t("EventDialog.labels.isNotArchived")
);

// Form validation
const validationSchema = yupObject({
    name: yupString().required().min(1).max(64),
    tag: yupString().required().min(1).max(8),
    date: yupDate().required(),
    archived: yupBoolean(),
    mainurl: yupString().required().url().max(200),
});
const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        name: "",
        tag: "",
        date: "",
        archived: false,
        mainurl: "",
    },
});
const name = useField<string>("name");
const tag = useField<string>("tag");
const date = useField<string>("date");
const archived = useField<boolean>("archived");
const mainurl = useField<string>("mainurl");

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
        await refreshEvents();
        goBack();
    }
});

async function createItem(values: GenericObject) {
    try {
        await api.adminEventsCreate({
            body: {
                name: values.name,
                date: values.date,
                archived: values.archived,
                tag: values.tag,
                mainurl: values.mainurl,
            },
        });
        toast.success(t("EventDialog.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("EventDialog.createFailure"));
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        await api.adminEventsPartialUpdate({
            path: { id: itemId },
            body: {
                name: values.name,
                date: values.date,
                archived: values.archived,
                tag: values.tag,
                mainurl: values.mainurl,
            },
        });
        toast.success(t("EventDialog.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("EventDialog.editFailure"));
    }
    return false;
}

function goBack() {
    router.push({ name: "events" });
}

onMounted(async () => {
    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminEventsRetrieve({
                path: { id: parseInt(props.id!, 10) },
            });
            const item = response.data!;
            eventName.value = item.name;
            setValues({
                name: item.name,
                tag: item.tag ?? "",
                date: item.date,
                archived: item.archived ?? false,
                mainurl: item.mainurl ?? "",
            });
        } catch (e) {
            toast.error(t("EventEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
