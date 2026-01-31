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
                            :label="t('CompoEditView.labels.name') + ' *'"
                        />
                        <VuetifyTiptap v-model="description.value.value" />
                        <div
                            v-if="description.errorMessage.value"
                            class="text-error text-caption mb-4"
                        >
                            {{ description.errorMessage.value }}
                        </div>

                        <FormSection>
                            {{ t("CompoEditView.sections.schedule") }}
                        </FormSection>
                        <v-row>
                            <v-col cols="12" md="6">
                                <v-text-field
                                    v-model="addingEnd.value.value"
                                    type="datetime-local"
                                    :error-messages="addingEnd.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompoEditView.labels.addingEnd') + ' *'"
                                />
                            </v-col>
                            <v-col cols="12" md="6">
                                <v-text-field
                                    v-model="editingEnd.value.value"
                                    type="datetime-local"
                                    :error-messages="editingEnd.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompoEditView.labels.editingEnd') + ' *'"
                                />
                            </v-col>
                        </v-row>
                        <v-row>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model="compoStart.value.value"
                                    type="datetime-local"
                                    :error-messages="compoStart.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompoEditView.labels.compoStart') + ' *'"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model="votingStart.value.value"
                                    type="datetime-local"
                                    :error-messages="votingStart.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompoEditView.labels.votingStart') + ' *'"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model="votingEnd.value.value"
                                    type="datetime-local"
                                    :error-messages="votingEnd.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompoEditView.labels.votingEnd') + ' *'"
                                />
                            </v-col>
                        </v-row>

                        <FormSection>
                            {{ t("CompoEditView.sections.fileSettings") }}
                        </FormSection>
                        <v-row>
                            <v-col cols="12" md="6">
                                <div class="d-flex ga-2">
                                    <v-text-field
                                        v-model.number="entrySizeValue"
                                        type="number"
                                        min="0"
                                        :error-messages="entrySizelimit.errorMessage.value"
                                        variant="outlined"
                                        :label="t('CompoEditView.labels.entrySizelimit')"
                                        class="flex-grow-1"
                                    />
                                    <v-select
                                        v-model="entrySizeUnit"
                                        :items="sizeUnitOptions"
                                        variant="outlined"
                                        style="max-width: 100px"
                                    />
                                </div>
                            </v-col>
                            <v-col cols="12" md="6">
                                <div class="d-flex ga-2">
                                    <v-text-field
                                        v-model.number="sourceSizeValue"
                                        type="number"
                                        min="0"
                                        :error-messages="sourceSizelimit.errorMessage.value"
                                        variant="outlined"
                                        :label="t('CompoEditView.labels.sourceSizelimit')"
                                        class="flex-grow-1"
                                    />
                                    <v-select
                                        v-model="sourceSizeUnit"
                                        :items="sizeUnitOptions"
                                        variant="outlined"
                                        style="max-width: 100px"
                                    />
                                </div>
                            </v-col>
                        </v-row>
                        <v-row>
                            <v-col cols="12" md="4">
                                <v-combobox
                                    v-model="formatsArray"
                                    :items="commonEntryFormats"
                                    :error-messages="formats.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompoEditView.labels.formats')"
                                    multiple
                                    chips
                                    closable-chips
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-combobox
                                    v-model="sourceFormatsArray"
                                    :items="commonSourceFormats"
                                    :error-messages="sourceFormats.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompoEditView.labels.sourceFormats')"
                                    multiple
                                    chips
                                    closable-chips
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-combobox
                                    v-model="imageFormatsArray"
                                    :items="commonImageFormats"
                                    :error-messages="imageFormats.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompoEditView.labels.imageFormats')"
                                    multiple
                                    chips
                                    closable-chips
                                />
                            </v-col>
                        </v-row>

                        <FormSection>
                            {{ t("CompoEditView.sections.displaySettings") }}
                        </FormSection>
                        <v-row>
                            <v-col cols="12" md="6">
                                <v-select
                                    v-model.number="entryViewType.value.value"
                                    :items="entryViewTypeOptions"
                                    :error-messages="entryViewType.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompoEditView.labels.entryViewType')"
                                >
                                    <template #item="{ props: itemProps, item }">
                                        <v-list-item v-bind="itemProps">
                                            <v-list-item-subtitle>
                                                {{ item.raw.description }}
                                            </v-list-item-subtitle>
                                        </v-list-item>
                                    </template>
                                </v-select>
                            </v-col>
                            <v-col cols="12" md="6">
                                <v-select
                                    v-model.number="thumbnailPref.value.value"
                                    :items="thumbnailPrefOptions"
                                    :error-messages="thumbnailPref.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompoEditView.labels.thumbnailPref')"
                                >
                                    <template #item="{ props: itemProps, item }">
                                        <v-list-item v-bind="itemProps">
                                            <v-list-item-subtitle>
                                                {{ item.raw.description }}
                                            </v-list-item-subtitle>
                                        </v-list-item>
                                    </template>
                                </v-select>
                            </v-col>
                        </v-row>

                        <FormSection>
                            {{ t("CompoEditView.sections.visibility") }}
                        </FormSection>
                        <ToggleSwitch
                            v-model="active.value.value"
                            :error-message="active.errorMessage.value"
                            :label-on="t('CompoEditView.labels.activeOn')"
                            :label-off="t('CompoEditView.labels.activeOff')"
                            :hint-on="t('CompoEditView.labels.activeHintOn')"
                            :hint-off="t('CompoEditView.labels.activeHintOff')"
                        />
                        <ToggleSwitch
                            v-model="isVotable.value.value"
                            :error-message="isVotable.errorMessage.value"
                            :label-on="t('CompoEditView.labels.isVotableOn')"
                            :label-off="t('CompoEditView.labels.isVotableOff')"
                            :hint-on="t('CompoEditView.labels.isVotableHintOn')"
                            :hint-off="t('CompoEditView.labels.isVotableHintOff')"
                        />
                        <ToggleSwitch
                            v-model="showVotingResults.value.value"
                            :error-message="showVotingResults.errorMessage.value"
                            :label-on="t('CompoEditView.labels.showVotingResultsOn')"
                            :label-off="t('CompoEditView.labels.showVotingResultsOff')"
                            :hint-on="t('CompoEditView.labels.showVotingResultsHintOn')"
                            :hint-off="t('CompoEditView.labels.showVotingResultsHintOff')"
                        />
                        <ToggleSwitch
                            v-model="showInArchive"
                            :error-message="hideFromArchive.errorMessage.value"
                            :label-on="t('CompoEditView.labels.hideFromArchiveOff')"
                            :label-off="t('CompoEditView.labels.hideFromArchiveOn')"
                            :hint-on="t('CompoEditView.labels.hideFromArchiveHintOn')"
                            :hint-off="t('CompoEditView.labels.hideFromArchiveHintOff')"
                        />
                        <ToggleSwitch
                            v-model="showOnFrontpage"
                            :error-message="hideFromFrontpage.errorMessage.value"
                            :label-on="t('CompoEditView.labels.hideFromFrontpageOff')"
                            :label-off="t('CompoEditView.labels.hideFromFrontpageOn')"
                            :hint-on="t('CompoEditView.labels.hideFromFrontpageHintOn')"
                            :hint-off="t('CompoEditView.labels.hideFromFrontpageHintOff')"
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
const compoName = ref<string>("");
const eventId = computed(() => parseInt(props.eventId, 10));
const isEditMode = computed(() => props.id !== undefined);

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = [
        {
            title: getEventById(eventId.value)?.name ?? "...",
            to: { name: "dashboard", params: { eventId: props.eventId } },
        },
        {
            title: t("ComposView.title"),
            to: { name: "compos", params: { eventId: props.eventId } },
        },
    ];
    if (isEditMode.value) {
        items.push({ title: compoName.value || "...", disabled: true });
    } else {
        items.push({ title: t("Breadcrumbs.newCompo"), disabled: true });
    }
    return items;
});

const entryViewTypeOptions = [
    {
        title: t("CompoEditView.entryViewTypes.0.title"),
        description: t("CompoEditView.entryViewTypes.0.description"),
        value: 0,
    },
    {
        title: t("CompoEditView.entryViewTypes.1.title"),
        description: t("CompoEditView.entryViewTypes.1.description"),
        value: 1,
    },
    {
        title: t("CompoEditView.entryViewTypes.2.title"),
        description: t("CompoEditView.entryViewTypes.2.description"),
        value: 2,
    },
];

const thumbnailPrefOptions = [
    {
        title: t("CompoEditView.thumbnailPrefs.0.title"),
        description: t("CompoEditView.thumbnailPrefs.0.description"),
        value: 0,
    },
    {
        title: t("CompoEditView.thumbnailPrefs.1.title"),
        description: t("CompoEditView.thumbnailPrefs.1.description"),
        value: 1,
    },
    {
        title: t("CompoEditView.thumbnailPrefs.2.title"),
        description: t("CompoEditView.thumbnailPrefs.2.description"),
        value: 2,
    },
    {
        title: t("CompoEditView.thumbnailPrefs.3.title"),
        description: t("CompoEditView.thumbnailPrefs.3.description"),
        value: 3,
    },
];

// Size unit options and conversion
type SizeUnit = "B" | "KB" | "MB" | "GB";
const sizeUnitOptions: SizeUnit[] = ["B", "KB", "MB", "GB"];
const sizeMultipliers: Record<SizeUnit, number> = {
    B: 1,
    KB: 1024,
    MB: 1024 * 1024,
    GB: 1024 * 1024 * 1024,
};

const entrySizeUnit = ref<SizeUnit>("MB");
const sourceSizeUnit = ref<SizeUnit>("MB");

// Convert bytes to display value based on unit
function bytesToUnit(bytes: number | null, unit: SizeUnit): number | null {
    if (bytes === null || bytes === undefined) return null;
    return Math.round((bytes / sizeMultipliers[unit]) * 100) / 100;
}

// Convert display value to bytes based on unit
function unitToBytes(value: number | null, unit: SizeUnit): number | null {
    if (value === null || value === undefined) return null;
    return Math.round(value * sizeMultipliers[unit]);
}

// Determine best unit for a byte value
function bestUnitForBytes(bytes: number | null): SizeUnit {
    if (bytes === null || bytes === undefined || bytes === 0) return "MB";
    if (bytes >= sizeMultipliers.GB) return "GB";
    if (bytes >= sizeMultipliers.MB) return "MB";
    if (bytes >= sizeMultipliers.KB) return "KB";
    return "B";
}

// Computed properties for size values
const entrySizeValue = computed({
    get: () => bytesToUnit(entrySizelimit.value.value, entrySizeUnit.value),
    set: (val) => {
        entrySizelimit.value.value = unitToBytes(val, entrySizeUnit.value);
    },
});

const sourceSizeValue = computed({
    get: () => bytesToUnit(sourceSizelimit.value.value, sourceSizeUnit.value),
    set: (val) => {
        sourceSizelimit.value.value = unitToBytes(val, sourceSizeUnit.value);
    },
});

// Common file formats
const commonEntryFormats = ["zip", "7z", "rar", "tar.gz", "exe", "com", "prg", "d64", "sid"];
const commonSourceFormats = ["zip", "7z", "rar", "tar.gz"];
const commonImageFormats = ["png", "jpg", "jpeg", "gif", "webp", "bmp"];

// Computed properties for format arrays (pipe-separated string <-> array)
const formatsArray = computed({
    get: () => (formats.value.value ? formats.value.value.split("|").filter(Boolean) : []),
    set: (val: string[]) => {
        formats.value.value = val.join("|");
    },
});

const sourceFormatsArray = computed({
    get: () =>
        sourceFormats.value.value ? sourceFormats.value.value.split("|").filter(Boolean) : [],
    set: (val: string[]) => {
        sourceFormats.value.value = val.join("|");
    },
});

const imageFormatsArray = computed({
    get: () =>
        imageFormats.value.value ? imageFormats.value.value.split("|").filter(Boolean) : [],
    set: (val: string[]) => {
        imageFormats.value.value = val.join("|");
    },
});

// Form validation
const validationSchema = yupObject({
    name: yupString().required().min(1).max(32),
    description: yupString(),
    addingEnd: yupString().required(),
    editingEnd: yupString().required(),
    compoStart: yupString().required(),
    votingStart: yupString().required(),
    votingEnd: yupString().required(),
    entrySizelimit: yupNumber().nullable(),
    sourceSizelimit: yupNumber().nullable(),
    formats: yupString(),
    sourceFormats: yupString(),
    imageFormats: yupString(),
    active: yupBoolean(),
    showVotingResults: yupBoolean(),
    isVotable: yupBoolean(),
    entryViewType: yupNumber(),
    thumbnailPref: yupNumber(),
    hideFromArchive: yupBoolean(),
    hideFromFrontpage: yupBoolean(),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        name: "",
        description: "",
        addingEnd: "",
        editingEnd: "",
        compoStart: "",
        votingStart: "",
        votingEnd: "",
        entrySizelimit: null as number | null,
        sourceSizelimit: null as number | null,
        formats: "",
        sourceFormats: "",
        imageFormats: "",
        active: true,
        showVotingResults: false,
        isVotable: true,
        entryViewType: 0,
        thumbnailPref: 0,
        hideFromArchive: false,
        hideFromFrontpage: false,
    },
});

const name = useField<string>("name");
const description = useField<string>("description");
const addingEnd = useField<string>("addingEnd");
const editingEnd = useField<string>("editingEnd");
const compoStart = useField<string>("compoStart");
const votingStart = useField<string>("votingStart");
const votingEnd = useField<string>("votingEnd");
const entrySizelimit = useField<number | null>("entrySizelimit");
const sourceSizelimit = useField<number | null>("sourceSizelimit");
const formats = useField<string>("formats");
const sourceFormats = useField<string>("sourceFormats");
const imageFormats = useField<string>("imageFormats");
const active = useField<boolean>("active");
const showVotingResults = useField<boolean>("showVotingResults");
const isVotable = useField<boolean>("isVotable");
const entryViewType = useField<number>("entryViewType");
const thumbnailPref = useField<number>("thumbnailPref");
const hideFromArchive = useField<boolean>("hideFromArchive");
const hideFromFrontpage = useField<boolean>("hideFromFrontpage");

// Inverted computed properties: toggle ON = visible (stores false in hideFrom fields)
const showInArchive = computed({
    get: () => !hideFromArchive.value.value,
    set: (val: boolean) => {
        hideFromArchive.value.value = !val;
    },
});
const showOnFrontpage = computed({
    get: () => !hideFromFrontpage.value.value,
    set: (val: boolean) => {
        hideFromFrontpage.value.value = !val;
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
        await api.adminEventKompomaattiComposCreate({
            path: { event_pk: eventId.value },
            body: {
                name: values.name,
                description: values.description || "",
                adding_end: toISODatetime(values.addingEnd)!,
                editing_end: toISODatetime(values.editingEnd)!,
                compo_start: toISODatetime(values.compoStart)!,
                voting_start: toISODatetime(values.votingStart)!,
                voting_end: toISODatetime(values.votingEnd)!,
                entry_sizelimit: values.entrySizelimit,
                source_sizelimit: values.sourceSizelimit,
                formats: values.formats || "",
                source_formats: values.sourceFormats || "",
                image_formats: values.imageFormats || "",
                active: values.active,
                show_voting_results: values.showVotingResults,
                is_votable: values.isVotable,
                entry_view_type: values.entryViewType,
                thumbnail_pref: values.thumbnailPref,
                hide_from_archive: values.hideFromArchive,
                hide_from_frontpage: values.hideFromFrontpage,
            },
        });
        toast.success(t("CompoEditView.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("CompoEditView.createFailure"), {
            name: "name",
            description: "description",
            adding_end: "addingEnd",
            editing_end: "editingEnd",
            compo_start: "compoStart",
            voting_start: "votingStart",
            voting_end: "votingEnd",
            entry_sizelimit: "entrySizelimit",
            source_sizelimit: "sourceSizelimit",
            formats: "formats",
            source_formats: "sourceFormats",
            image_formats: "imageFormats",
            active: "active",
            show_voting_results: "showVotingResults",
            is_votable: "isVotable",
            entry_view_type: "entryViewType",
            thumbnail_pref: "thumbnailPref",
            hide_from_archive: "hideFromArchive",
            hide_from_frontpage: "hideFromFrontpage",
        });
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        await api.adminEventKompomaattiComposPartialUpdate({
            path: { event_pk: eventId.value, id: itemId },
            body: {
                name: values.name,
                description: values.description || "",
                adding_end: toISODatetime(values.addingEnd)!,
                editing_end: toISODatetime(values.editingEnd)!,
                compo_start: toISODatetime(values.compoStart)!,
                voting_start: toISODatetime(values.votingStart)!,
                voting_end: toISODatetime(values.votingEnd)!,
                entry_sizelimit: values.entrySizelimit,
                source_sizelimit: values.sourceSizelimit,
                formats: values.formats || "",
                source_formats: values.sourceFormats || "",
                image_formats: values.imageFormats || "",
                active: values.active,
                show_voting_results: values.showVotingResults,
                is_votable: values.isVotable,
                entry_view_type: values.entryViewType,
                thumbnail_pref: values.thumbnailPref,
                hide_from_archive: values.hideFromArchive,
                hide_from_frontpage: values.hideFromFrontpage,
            },
        });
        toast.success(t("CompoEditView.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("CompoEditView.editFailure"), {
            name: "name",
            description: "description",
            adding_end: "addingEnd",
            editing_end: "editingEnd",
            compo_start: "compoStart",
            voting_start: "votingStart",
            voting_end: "votingEnd",
            entry_sizelimit: "entrySizelimit",
            source_sizelimit: "sourceSizelimit",
            formats: "formats",
            source_formats: "sourceFormats",
            image_formats: "imageFormats",
            active: "active",
            show_voting_results: "showVotingResults",
            is_votable: "isVotable",
            entry_view_type: "entryViewType",
            thumbnail_pref: "thumbnailPref",
            hide_from_archive: "hideFromArchive",
            hide_from_frontpage: "hideFromFrontpage",
        });
    }
    return false;
}

function goBack() {
    router.push({ name: "compos", params: { eventId: props.eventId } });
}

onMounted(async () => {
    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminEventKompomaattiComposRetrieve({
                path: { event_pk: eventId.value, id: parseInt(props.id!, 10) },
            });
            const item = response.data!;
            compoName.value = item.name;
            // Set appropriate units for file sizes
            entrySizeUnit.value = bestUnitForBytes(item.entry_sizelimit ?? null);
            sourceSizeUnit.value = bestUnitForBytes(item.source_sizelimit ?? null);
            setValues({
                name: item.name,
                description: item.description ?? "",
                addingEnd: toLocalDatetime(item.adding_end),
                editingEnd: toLocalDatetime(item.editing_end),
                compoStart: toLocalDatetime(item.compo_start),
                votingStart: toLocalDatetime(item.voting_start),
                votingEnd: toLocalDatetime(item.voting_end),
                entrySizelimit: item.entry_sizelimit ?? null,
                sourceSizelimit: item.source_sizelimit ?? null,
                formats: item.formats ?? "",
                sourceFormats: item.source_formats ?? "",
                imageFormats: item.image_formats ?? "",
                active: item.active ?? true,
                showVotingResults: item.show_voting_results ?? false,
                isVotable: item.is_votable ?? true,
                entryViewType: item.entry_view_type ?? 0,
                thumbnailPref: item.thumbnail_pref ?? 0,
                hideFromArchive: item.hide_from_archive ?? false,
                hideFromFrontpage: item.hide_from_frontpage ?? false,
            });
        } catch (e) {
            toast.error(t("CompoEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
