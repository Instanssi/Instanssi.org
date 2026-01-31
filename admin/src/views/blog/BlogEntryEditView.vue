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
                            v-model="title.value.value"
                            :error-messages="title.errorMessage.value"
                            variant="outlined"
                            :label="t('BlogPostDialog.labels.title') + ' *'"
                        />
                        <div class="text-subtitle-2 mb-1">
                            {{ t("BlogPostDialog.labels.text") }} *
                        </div>
                        <VuetifyTiptap v-model="text.value.value" />
                        <div v-if="text.errorMessage.value" class="text-error text-caption">
                            {{ text.errorMessage.value }}
                        </div>
                        <v-switch
                            v-model="isPublic.value.value"
                            :error-messages="isPublic.errorMessage.value"
                            :label="switchLabel"
                            :class="{ 'text-green-darken-3': isPublic.value.value }"
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
import { boolean as yupBoolean, object as yupObject, string as yupString } from "yup";

import * as api from "@/api";
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
const entryTitle = ref<string>("");
const eventId = computed(() => parseInt(props.eventId, 10));
const isEditMode = computed(() => props.id !== undefined);

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = [
        {
            title: getEventById(eventId.value)?.name ?? "...",
            to: { name: "dashboard", params: { eventId: props.eventId } },
        },
        {
            title: t("BlogEditorView.title"),
            to: { name: "blog", params: { eventId: props.eventId } },
        },
    ];
    if (isEditMode.value) {
        items.push({ title: entryTitle.value || "...", disabled: true });
    } else {
        items.push({ title: t("Breadcrumbs.newPost"), disabled: true });
    }
    return items;
});
const switchLabel = computed(() =>
    isPublic.value.value
        ? t("BlogPostDialog.labels.postIsVisible")
        : t("BlogPostDialog.labels.postNotVisible")
);

// Form validation
const validationSchema = yupObject({
    title: yupString().required().min(1).max(128),
    text: yupString().required().min(1),
    public: yupBoolean(),
});
const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        title: "",
        text: "",
        public: false,
    },
});
const title = useField<string>("title");
const text = useField<string>("text");
const isPublic = useField<boolean>("public");

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
    try {
        await api.adminBlogCreate({
            body: {
                event: parseInt(props.eventId, 10),
                title: values.title,
                text: values.text,
                public: values.public,
            },
        });
        toast.success(t("BlogPostDialog.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("BlogPostDialog.createFailure"), {
            title: "title",
            text: "text",
            public: "public",
        });
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        await api.adminBlogPartialUpdate({
            path: { id: itemId },
            body: {
                title: values.title,
                text: values.text,
                public: values.public,
            },
        });
        toast.success(t("BlogPostDialog.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("BlogPostDialog.editFailure"), {
            title: "title",
            text: "text",
            public: "public",
        });
    }
    return false;
}

function goBack() {
    router.push({ name: "blog", params: { eventId: props.eventId } });
}

onMounted(async () => {
    // Fetch blog entry if editing
    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminBlogRetrieve({ path: { id: parseInt(props.id!, 10) } });
            const item = response.data!;
            entryTitle.value = item.title;
            setValues({
                title: item.title,
                text: item.text,
                public: item.public ?? false,
            });
        } catch (e) {
            toast.error(t("BlogEntryEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
