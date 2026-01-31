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
                            {{ t("ProgramEventEditView.sections.basic") }}
                        </FormSection>
                        <v-text-field
                            v-model="title.value.value"
                            :error-messages="title.errorMessage.value"
                            variant="outlined"
                            :label="t('ProgramEventEditView.labels.title') + ' *'"
                        />
                        <v-textarea
                            v-model="description.value.value"
                            :error-messages="description.errorMessage.value"
                            variant="outlined"
                            :label="t('ProgramEventEditView.labels.description')"
                            rows="4"
                        />
                        <v-row>
                            <v-col cols="12" md="6">
                                <v-text-field
                                    v-model="start.value.value"
                                    type="datetime-local"
                                    :error-messages="start.errorMessage.value"
                                    variant="outlined"
                                    :label="t('ProgramEventEditView.labels.start') + ' *'"
                                />
                            </v-col>
                            <v-col cols="12" md="6">
                                <v-text-field
                                    v-model="end.value.value"
                                    type="datetime-local"
                                    :error-messages="end.errorMessage.value"
                                    variant="outlined"
                                    :label="t('ProgramEventEditView.labels.end')"
                                />
                            </v-col>
                        </v-row>
                        <v-text-field
                            v-model="place.value.value"
                            :error-messages="place.errorMessage.value"
                            variant="outlined"
                            :label="t('ProgramEventEditView.labels.place')"
                        />

                        <template v-if="isDetailedEvent">
                            <FormSection>
                                {{ t("ProgramEventEditView.sections.presenters") }}
                            </FormSection>
                            <v-text-field
                                v-model="presenters.value.value"
                                :error-messages="presenters.errorMessage.value"
                                variant="outlined"
                                :label="t('ProgramEventEditView.labels.presenters')"
                            />
                            <v-text-field
                                v-model="presentersTitles.value.value"
                                :error-messages="presentersTitles.errorMessage.value"
                                variant="outlined"
                                :label="t('ProgramEventEditView.labels.presentersTitles')"
                            />

                            <FormSection>
                                {{ t("ProgramEventEditView.sections.images") }}
                            </FormSection>
                            <v-row>
                                <v-col cols="12" md="6">
                                    <v-file-input
                                        v-model="icon1File.value.value"
                                        :label="t('ProgramEventEditView.labels.icon1')"
                                        :error-messages="icon1File.errorMessage.value"
                                        variant="outlined"
                                        accept="image/*"
                                        prepend-icon=""
                                        clearable
                                    >
                                        <template #prepend>
                                            <FontAwesomeIcon :icon="faImage" />
                                        </template>
                                    </v-file-input>
                                    <v-img
                                        v-if="currentIcon1Url"
                                        :src="currentIcon1Url"
                                        max-width="200"
                                        class="mb-4"
                                    />
                                </v-col>
                                <v-col cols="12" md="6">
                                    <v-file-input
                                        v-model="icon2File.value.value"
                                        :label="t('ProgramEventEditView.labels.icon2')"
                                        :error-messages="icon2File.errorMessage.value"
                                        variant="outlined"
                                        accept="image/*"
                                        prepend-icon=""
                                        clearable
                                    >
                                        <template #prepend>
                                            <FontAwesomeIcon :icon="faImage" />
                                        </template>
                                    </v-file-input>
                                    <v-img
                                        v-if="currentIcon2Url"
                                        :src="currentIcon2Url"
                                        max-width="200"
                                        class="mb-4"
                                    />
                                </v-col>
                            </v-row>

                            <FormSection>
                                {{ t("ProgramEventEditView.sections.links") }}
                            </FormSection>
                            <v-row>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model="homeUrl.value.value"
                                        :error-messages="homeUrl.errorMessage.value"
                                        variant="outlined"
                                        :label="t('ProgramEventEditView.labels.homeUrl')"
                                        type="url"
                                    />
                                </v-col>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model="email.value.value"
                                        :error-messages="email.errorMessage.value"
                                        variant="outlined"
                                        :label="t('ProgramEventEditView.labels.email')"
                                        type="email"
                                    />
                                </v-col>
                            </v-row>
                            <v-row>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model="twitterUrl.value.value"
                                        :error-messages="twitterUrl.errorMessage.value"
                                        variant="outlined"
                                        :label="t('ProgramEventEditView.labels.twitterUrl')"
                                        type="url"
                                    />
                                </v-col>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model="githubUrl.value.value"
                                        :error-messages="githubUrl.errorMessage.value"
                                        variant="outlined"
                                        :label="t('ProgramEventEditView.labels.githubUrl')"
                                        type="url"
                                    />
                                </v-col>
                            </v-row>
                            <v-row>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model="facebookUrl.value.value"
                                        :error-messages="facebookUrl.errorMessage.value"
                                        variant="outlined"
                                        :label="t('ProgramEventEditView.labels.facebookUrl')"
                                        type="url"
                                    />
                                </v-col>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model="linkedinUrl.value.value"
                                        :error-messages="linkedinUrl.errorMessage.value"
                                        variant="outlined"
                                        :label="t('ProgramEventEditView.labels.linkedinUrl')"
                                        type="url"
                                    />
                                </v-col>
                            </v-row>
                            <v-text-field
                                v-model="wikiUrl.value.value"
                                :error-messages="wikiUrl.errorMessage.value"
                                variant="outlined"
                                :label="t('ProgramEventEditView.labels.wikiUrl')"
                                type="url"
                            />
                        </template>

                        <FormSection>
                            {{ t("ProgramEventEditView.sections.settings") }}
                        </FormSection>
                        <ToggleSwitch
                            v-model="isDetailedEvent"
                            :label-on="t('ProgramEventEditView.labels.eventTypeDetailedOn')"
                            :label-off="t('ProgramEventEditView.labels.eventTypeDetailedOff')"
                            :hint-on="t('ProgramEventEditView.labels.eventTypeDetailedHintOn')"
                            :hint-off="t('ProgramEventEditView.labels.eventTypeDetailedHintOff')"
                        />
                        <ToggleSwitch
                            v-model="active.value.value"
                            :error-message="active.errorMessage.value"
                            :label-on="t('ProgramEventEditView.labels.activeOn')"
                            :label-off="t('ProgramEventEditView.labels.activeOff')"
                            :hint-on="t('ProgramEventEditView.labels.activeHintOn')"
                            :hint-off="t('ProgramEventEditView.labels.activeHintOff')"
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
import { faFloppyDisk as faSave, faImage } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { parseInt } from "lodash-es";
import { type GenericObject, useField, useForm } from "vee-validate";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import {
    boolean as yupBoolean,
    mixed as yupMixed,
    number as yupNumber,
    object as yupObject,
    string as yupString,
} from "yup";

import * as api from "@/api";
import FormSection from "@/components/form/FormSection.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import ToggleSwitch from "@/components/form/ToggleSwitch.vue";
import { useEvents } from "@/services/events";
import { toISODatetime, toLocalDatetime } from "@/utils/datetime";
import { type FileValue, getFile } from "@/utils/file";
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
const itemTitle = ref<string>("");
const eventId = computed(() => parseInt(props.eventId, 10));
const isEditMode = computed(() => props.id !== undefined);
const currentIcon1Url = ref<string | null>(null);
const currentIcon2Url = ref<string | null>(null);

// Computed property to map event_type (0 = Simple, 1 = Detailed) to boolean toggle
const isDetailedEvent = computed({
    get: () => eventType.value.value === 1,
    set: (val: boolean) => {
        eventType.value.value = val ? 1 : 0;
    },
});

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = [
        {
            title: getEventById(eventId.value)?.name ?? "...",
            to: { name: "dashboard", params: { eventId: props.eventId } },
        },
        {
            title: t("ProgramEventsView.title"),
            to: { name: "program", params: { eventId: props.eventId } },
        },
    ];
    if (isEditMode.value) {
        items.push({ title: itemTitle.value || "...", disabled: true });
    } else {
        items.push({ title: t("Breadcrumbs.newProgramEvent"), disabled: true });
    }
    return items;
});

// Form validation
const validationSchema = yupObject({
    title: yupString().required().min(1).max(64),
    description: yupString(),
    start: yupString().required(),
    end: yupString().nullable(),
    place: yupString().max(64),
    presenters: yupString().max(256),
    presentersTitles: yupString().max(256),
    homeUrl: yupString().url().max(255),
    email: yupString().email().max(128),
    twitterUrl: yupString().url().max(255),
    githubUrl: yupString().url().max(255),
    facebookUrl: yupString().url().max(255),
    linkedinUrl: yupString().url().max(255),
    wikiUrl: yupString().url().max(255),
    eventType: yupNumber().oneOf([0, 1]),
    active: yupBoolean(),
    icon1File: yupMixed().nullable(),
    icon2File: yupMixed().nullable(),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        title: "",
        description: "",
        start: "",
        end: "",
        place: "",
        presenters: "",
        presentersTitles: "",
        homeUrl: "",
        email: "",
        twitterUrl: "",
        githubUrl: "",
        facebookUrl: "",
        linkedinUrl: "",
        wikiUrl: "",
        eventType: 0,
        active: true,
        icon1File: null as FileValue,
        icon2File: null as FileValue,
    },
});

const title = useField<string>("title");
const description = useField<string>("description");
const start = useField<string>("start");
const end = useField<string>("end");
const place = useField<string>("place");
const presenters = useField<string>("presenters");
const presentersTitles = useField<string>("presentersTitles");
const homeUrl = useField<string>("homeUrl");
const email = useField<string>("email");
const twitterUrl = useField<string>("twitterUrl");
const githubUrl = useField<string>("githubUrl");
const facebookUrl = useField<string>("facebookUrl");
const linkedinUrl = useField<string>("linkedinUrl");
const wikiUrl = useField<string>("wikiUrl");
const eventType = useField<number>("eventType");
const active = useField<boolean>("active");
const icon1File = useField<FileValue>("icon1File");
const icon2File = useField<FileValue>("icon2File");

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
        // Always use FormData for this endpoint (supports optional file uploads)
        await api.adminEventProgramEventsCreate({
            path: { event_pk: eventId.value },
            body: {
                title: values.title,
                description: values.description || "",
                start: toISODatetime(values.start)!,
                end: toISODatetime(values.end) ?? undefined,
                place: values.place || "",
                presenters: values.presenters || "",
                presenters_titles: values.presentersTitles || "",
                home_url: values.homeUrl || "",
                email: values.email || "",
                twitter_url: values.twitterUrl || "",
                github_url: values.githubUrl || "",
                facebook_url: values.facebookUrl || "",
                linkedin_url: values.linkedinUrl || "",
                wiki_url: values.wikiUrl || "",
                event_type: values.eventType,
                active: values.active,
                icon_original: getFile(values.icon1File),
                icon2_original: getFile(values.icon2File),
            },
            bodySerializer: (body) => {
                const formData = new FormData();
                formData.append("title", body.title);
                formData.append("description", body.description || "");
                formData.append("start", body.start);
                if (body.end) formData.append("end", body.end);
                formData.append("place", body.place || "");
                formData.append("presenters", body.presenters || "");
                formData.append("presenters_titles", body.presenters_titles || "");
                formData.append("home_url", body.home_url || "");
                formData.append("email", body.email || "");
                formData.append("twitter_url", body.twitter_url || "");
                formData.append("github_url", body.github_url || "");
                formData.append("facebook_url", body.facebook_url || "");
                formData.append("linkedin_url", body.linkedin_url || "");
                formData.append("wiki_url", body.wiki_url || "");
                formData.append("event_type", String(body.event_type ?? 0));
                formData.append("active", body.active ? "true" : "false");
                if (body.icon_original) formData.append("icon_original", body.icon_original);
                if (body.icon2_original) formData.append("icon2_original", body.icon2_original);
                return formData;
            },
        });
        toast.success(t("ProgramEventEditView.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("ProgramEventEditView.createFailure"), {
            title: "title",
            description: "description",
            start: "start",
            end: "end",
            place: "place",
            presenters: "presenters",
            presenters_titles: "presentersTitles",
            icon_original: "icon1File",
            icon2_original: "icon2File",
            home_url: "homeUrl",
            email: "email",
            twitter_url: "twitterUrl",
            github_url: "githubUrl",
            facebook_url: "facebookUrl",
            linkedin_url: "linkedinUrl",
            wiki_url: "wikiUrl",
            event_type: "eventType",
            active: "active",
        });
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        // Always use FormData for this endpoint (supports optional file uploads)
        await api.adminEventProgramEventsPartialUpdate({
            path: { event_pk: eventId.value, id: itemId },
            body: {
                title: values.title,
                description: values.description || "",
                start: toISODatetime(values.start)!,
                end: toISODatetime(values.end) ?? undefined,
                place: values.place || "",
                presenters: values.presenters || "",
                presenters_titles: values.presentersTitles || "",
                home_url: values.homeUrl || "",
                email: values.email || "",
                twitter_url: values.twitterUrl || "",
                github_url: values.githubUrl || "",
                facebook_url: values.facebookUrl || "",
                linkedin_url: values.linkedinUrl || "",
                wiki_url: values.wikiUrl || "",
                event_type: values.eventType,
                active: values.active,
                icon_original: getFile(values.icon1File),
                icon2_original: getFile(values.icon2File),
            },
            bodySerializer: (body) => {
                const formData = new FormData();
                formData.append("title", body.title);
                formData.append("description", body.description || "");
                formData.append("start", body.start);
                if (body.end) formData.append("end", body.end);
                formData.append("place", body.place || "");
                formData.append("presenters", body.presenters || "");
                formData.append("presenters_titles", body.presenters_titles || "");
                formData.append("home_url", body.home_url || "");
                formData.append("email", body.email || "");
                formData.append("twitter_url", body.twitter_url || "");
                formData.append("github_url", body.github_url || "");
                formData.append("facebook_url", body.facebook_url || "");
                formData.append("linkedin_url", body.linkedin_url || "");
                formData.append("wiki_url", body.wiki_url || "");
                formData.append("event_type", String(body.event_type ?? 0));
                formData.append("active", body.active ? "true" : "false");
                if (body.icon_original) formData.append("icon_original", body.icon_original);
                if (body.icon2_original) formData.append("icon2_original", body.icon2_original);
                return formData;
            },
        });
        toast.success(t("ProgramEventEditView.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("ProgramEventEditView.editFailure"), {
            title: "title",
            description: "description",
            start: "start",
            end: "end",
            place: "place",
            presenters: "presenters",
            presenters_titles: "presentersTitles",
            icon_original: "icon1File",
            icon2_original: "icon2File",
            home_url: "homeUrl",
            email: "email",
            twitter_url: "twitterUrl",
            github_url: "githubUrl",
            facebook_url: "facebookUrl",
            linkedin_url: "linkedinUrl",
            wiki_url: "wikiUrl",
            event_type: "eventType",
            active: "active",
        });
    }
    return false;
}

function goBack() {
    router.push({ name: "program", params: { eventId: props.eventId } });
}

onMounted(async () => {
    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminEventProgramEventsRetrieve({
                path: { event_pk: eventId.value, id: parseInt(props.id!, 10) },
            });
            const item = response.data!;
            itemTitle.value = item.title;
            currentIcon1Url.value = item.icon_small_url ?? null;
            currentIcon2Url.value = item.icon2_small_url ?? null;
            setValues({
                title: item.title,
                description: item.description ?? "",
                start: toLocalDatetime(item.start),
                end: toLocalDatetime(item.end),
                place: item.place ?? "",
                presenters: item.presenters ?? "",
                presentersTitles: item.presenters_titles ?? "",
                homeUrl: item.home_url ?? "",
                email: item.email ?? "",
                twitterUrl: item.twitter_url ?? "",
                githubUrl: item.github_url ?? "",
                facebookUrl: item.facebook_url ?? "",
                linkedinUrl: item.linkedin_url ?? "",
                wikiUrl: item.wiki_url ?? "",
                eventType: item.event_type ?? 0,
                active: item.active ?? true,
            });
        } catch (e) {
            toast.error(t("ProgramEventEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
