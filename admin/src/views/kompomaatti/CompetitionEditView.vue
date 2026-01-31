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
                            :label="t('CompetitionEditView.labels.name') + ' *'"
                        />
                        <v-textarea
                            v-model="description.value.value"
                            :error-messages="description.errorMessage.value"
                            variant="outlined"
                            :label="t('CompetitionEditView.labels.description')"
                            rows="3"
                        />

                        <FormSection>
                            {{ t("CompetitionEditView.sections.schedule") }}
                        </FormSection>
                        <v-row>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model="participationEnd.value.value"
                                    type="datetime-local"
                                    :error-messages="participationEnd.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompetitionEditView.labels.participationEnd') + ' *'"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model="start.value.value"
                                    type="datetime-local"
                                    :error-messages="start.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompetitionEditView.labels.start') + ' *'"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model="end.value.value"
                                    type="datetime-local"
                                    :error-messages="end.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompetitionEditView.labels.end')"
                                />
                            </v-col>
                        </v-row>

                        <FormSection>
                            {{ t("CompetitionEditView.sections.scoring") }}
                        </FormSection>
                        <v-row>
                            <v-col cols="12" md="6">
                                <v-combobox
                                    v-model="scoreType.value.value"
                                    :items="commonScoreTypes"
                                    :error-messages="scoreType.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompetitionEditView.labels.scoreType') + ' *'"
                                />
                            </v-col>
                            <v-col cols="12" md="6">
                                <v-select
                                    v-model.number="scoreSort.value.value"
                                    :items="scoreSortOptions"
                                    :error-messages="scoreSort.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompetitionEditView.labels.scoreSort')"
                                />
                            </v-col>
                        </v-row>

                        <FormSection>
                            {{ t("CompetitionEditView.sections.settings") }}
                        </FormSection>
                        <ToggleSwitch
                            v-model="active.value.value"
                            :error-message="active.errorMessage.value"
                            :label-on="t('CompetitionEditView.labels.activeOn')"
                            :label-off="t('CompetitionEditView.labels.activeOff')"
                            :hint-on="t('CompetitionEditView.labels.activeHintOn')"
                            :hint-off="t('CompetitionEditView.labels.activeHintOff')"
                        />
                        <ToggleSwitch
                            v-model="showResults.value.value"
                            :error-message="showResults.errorMessage.value"
                            :label-on="t('CompetitionEditView.labels.showResultsOn')"
                            :label-off="t('CompetitionEditView.labels.showResultsOff')"
                            :hint-on="t('CompetitionEditView.labels.showResultsHintOn')"
                            :hint-off="t('CompetitionEditView.labels.showResultsHintOff')"
                        />
                        <ToggleSwitch
                            v-model="showInArchive"
                            :error-message="hideFromArchive.errorMessage.value"
                            :label-on="t('CompetitionEditView.labels.hideFromArchiveOff')"
                            :label-off="t('CompetitionEditView.labels.hideFromArchiveOn')"
                            :hint-on="t('CompetitionEditView.labels.hideFromArchiveHintOn')"
                            :hint-off="t('CompetitionEditView.labels.hideFromArchiveHintOff')"
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
    boolean as yupBoolean,
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
const competitionName = ref<string>("");
const eventId = computed(() => parseInt(props.eventId, 10));
const isEditMode = computed(() => props.id !== undefined);

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = [
        {
            title: getEventById(eventId.value)?.name ?? "...",
            to: { name: "dashboard", params: { eventId: props.eventId } },
        },
        {
            title: t("CompetitionsView.title"),
            to: { name: "competitions", params: { eventId: props.eventId } },
        },
    ];
    if (isEditMode.value) {
        items.push({ title: competitionName.value || "...", disabled: true });
    } else {
        items.push({ title: t("Breadcrumbs.newCompetition"), disabled: true });
    }
    return items;
});

const scoreSortOptions = [
    { title: t("CompetitionEditView.scoreSortOptions.highestFirst"), value: 0 },
    { title: t("CompetitionEditView.scoreSortOptions.lowestFirst"), value: 1 },
];

// Common score types for combobox
const commonScoreTypes = ["pts", "sec", "min", "m", "km", "kg", "pcs"];

// Form validation
const validationSchema = yupObject({
    name: yupString().required().min(1).max(32),
    description: yupString(),
    participationEnd: yupString().required(),
    start: yupString().required(),
    end: yupString().nullable(),
    scoreType: yupString().required().max(8),
    scoreSort: yupNumber(),
    active: yupBoolean(),
    showResults: yupBoolean(),
    hideFromArchive: yupBoolean(),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        name: "",
        description: "",
        participationEnd: "",
        start: "",
        end: "",
        scoreType: "",
        scoreSort: 0,
        active: true,
        showResults: false,
        hideFromArchive: false,
    },
});

const name = useField<string>("name");
const description = useField<string>("description");
const participationEnd = useField<string>("participationEnd");
const start = useField<string>("start");
const end = useField<string>("end");
const scoreType = useField<string>("scoreType");
const scoreSort = useField<number>("scoreSort");
const active = useField<boolean>("active");
const showResults = useField<boolean>("showResults");
const hideFromArchive = useField<boolean>("hideFromArchive");

// Inverted computed property: toggle ON = visible (stores false in hideFromArchive)
const showInArchive = computed({
    get: () => !hideFromArchive.value.value,
    set: (val: boolean) => {
        hideFromArchive.value.value = !val;
    },
});

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
        await api.adminEventKompomaattiCompetitionsCreate({
            path: { event_pk: eventId.value },
            body: {
                name: values.name,
                description: values.description || "",
                participation_end: toISODatetime(values.participationEnd)!,
                start: toISODatetime(values.start)!,
                end: toISODatetime(values.end),
                score_type: values.scoreType,
                score_sort: values.scoreSort,
                active: values.active,
                show_results: values.showResults,
                hide_from_archive: values.hideFromArchive,
            },
        });
        toast.success(t("CompetitionEditView.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("CompetitionEditView.createFailure"));
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        await api.adminEventKompomaattiCompetitionsPartialUpdate({
            path: { event_pk: eventId.value, id: itemId },
            body: {
                name: values.name,
                description: values.description || "",
                participation_end: toISODatetime(values.participationEnd)!,
                start: toISODatetime(values.start)!,
                end: toISODatetime(values.end),
                score_type: values.scoreType,
                score_sort: values.scoreSort,
                active: values.active,
                show_results: values.showResults,
                hide_from_archive: values.hideFromArchive,
            },
        });
        toast.success(t("CompetitionEditView.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("CompetitionEditView.editFailure"));
    }
    return false;
}

function goBack() {
    router.push({ name: "competitions", params: { eventId: props.eventId } });
}

onMounted(async () => {
    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminEventKompomaattiCompetitionsRetrieve({
                path: { event_pk: eventId.value, id: parseInt(props.id!, 10) },
            });
            const item = response.data!;
            competitionName.value = item.name;
            setValues({
                name: item.name,
                description: item.description ?? "",
                participationEnd: toLocalDatetime(item.participation_end),
                start: toLocalDatetime(item.start),
                end: toLocalDatetime(item.end),
                scoreType: item.score_type ?? "",
                scoreSort: item.score_sort ?? 0,
                active: item.active ?? true,
                showResults: item.show_results ?? false,
                hideFromArchive: item.hide_from_archive ?? false,
            });
        } catch (e) {
            toast.error(t("CompetitionEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
