<template>
    <BaseDialog ref="dialog" :title="t('DiplomaGenerator.title')" :width="600">
        <v-card-text>
            <ImageSelectField
                v-model="selectedBackground"
                :items="backgroundOptions"
                :label="t('DiplomaGenerator.backgroundImage')"
                :placeholder="t('DiplomaGenerator.selectBackground')"
                :no-data-text="t('DiplomaGenerator.noImagesFound')"
                :loading="loadingUploads"
            />

            <v-divider class="my-4" />

            <div class="mb-4">
                <div class="text-subtitle-2 mb-2">{{ t("DiplomaGenerator.includeIn") }}</div>
                <v-checkbox
                    v-model="includeCompos"
                    :label="t('DiplomaGenerator.includeCompos')"
                    density="compact"
                    hide-details
                />
                <v-checkbox
                    v-model="includeCompetitions"
                    :label="t('DiplomaGenerator.includeCompetitions')"
                    density="compact"
                    hide-details
                />
            </div>

            <v-divider class="my-4" />

            <v-text-field
                v-model="mainOrganizerName"
                :label="t('DiplomaGenerator.mainOrganizerName')"
                variant="outlined"
                density="compact"
            />
            <v-text-field
                v-model="mainOrganizerTitle"
                :label="t('DiplomaGenerator.mainOrganizer')"
                variant="outlined"
                density="compact"
            />

            <v-divider class="my-4" />

            <v-text-field
                v-model="programOrganizerName"
                :label="t('DiplomaGenerator.programOrganizerName')"
                variant="outlined"
                density="compact"
            />
            <v-text-field
                v-model="programOrganizerTitle"
                :label="t('DiplomaGenerator.programOrganizer')"
                variant="outlined"
                density="compact"
            />

            <v-alert v-if="noEntriesWarning" type="warning" variant="tonal" class="mt-4">
                {{ t("DiplomaGenerator.noEntries") }}
            </v-alert>
        </v-card-text>
        <v-card-actions class="justify-end">
            <span
                v-if="generating && progressTotal > 0"
                class="text-body-2 text-medium-emphasis mr-4"
            >
                {{
                    t("DiplomaGenerator.generating", {
                        current: progressCurrent,
                        total: progressTotal,
                    })
                }}
            </span>
            <v-btn variant="text" @click="close">
                {{ t("General.cancel") }}
            </v-btn>
            <v-btn
                variant="elevated"
                color="primary"
                :loading="generating"
                :disabled="!canGenerate"
                @click="generateAll"
            >
                <template #prepend>
                    <FontAwesomeIcon :icon="faFilePdf" />
                </template>
                {{ t("DiplomaGenerator.generateAll") }}
            </v-btn>
        </v-card-actions>
    </BaseDialog>
</template>

<script setup lang="ts">
import { faFilePdf } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, ref, watch, type Ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";

import * as api from "@/api";
import type { Compo, CompoEntry, Competition, CompetitionParticipation, UploadedFile } from "@/api";
import BaseDialog from "@/components/dialogs/BaseDialog.vue";
import ImageSelectField from "@/components/form/ImageSelectField.vue";
import { useEvents } from "@/services/events";
import {
    generateAllDiplomasPdf,
    hasMultipleAuthors,
    type DiplomaData,
    type DiplomaOrganizers,
} from "@/utils/diploma";
import { toRomanNumeral } from "@/utils/roman";

const props = defineProps<{
    eventId: number;
}>();

const emit = defineEmits<{
    close: [];
}>();

const { t } = useI18n();
const toast = useToast();
const { getEventById } = useEvents();

const dialog: Ref<InstanceType<typeof BaseDialog> | undefined> = ref(undefined);
const loadingUploads = ref(false);
const generating = ref(false);
const progressCurrent = ref(0);
const progressTotal = ref(0);
const uploads: Ref<UploadedFile[]> = ref([]);
const entries: Ref<CompoEntry[]> = ref([]);
const compos: Ref<Compo[]> = ref([]);
const competitions: Ref<Competition[]> = ref([]);
const participations: Ref<CompetitionParticipation[]> = ref([]);

const selectedBackground: Ref<string | null> = ref(null);
const mainOrganizerName = ref("");
const mainOrganizerTitle = ref("Pääjärjestäjä");
const programOrganizerName = ref("");
const programOrganizerTitle = ref("Ohjelmavastaava");

defineExpose({ open });

const includeCompos = ref(true);
const includeCompetitions = ref(true);

// Filter uploads to only show supported image files (pdf-lib only supports PNG and JPEG)
const imageExtensions = ["png", "jpg", "jpeg"];
const backgroundOptions = computed(() => {
    return uploads.value
        .filter((upload) => {
            const ext = upload.filename.split(".").pop()?.toLowerCase() ?? "";
            return imageExtensions.includes(ext);
        })
        .map((upload) => ({
            title: upload.filename,
            value: upload.file_url,
        }));
});

const eventName = computed(() => getEventById(props.eventId)?.name ?? "");

// Build diploma data from entries and/or competition participations based on mode
const diplomaDataList = computed<DiplomaData[]>(() => {
    const organizers: DiplomaOrganizers = {
        mainOrganizer: { name: mainOrganizerName.value, title: mainOrganizerTitle.value },
        programOrganizer: { name: programOrganizerName.value, title: programOrganizerTitle.value },
    };

    const result: DiplomaData[] = [];

    // Process compo entries (if mode includes compos)
    if (includeCompos.value) {
        const entriesByCompo = new Map<number, CompoEntry[]>();
        for (const entry of entries.value) {
            const compoEntries = entriesByCompo.get(entry.compo) ?? [];
            compoEntries.push(entry);
            entriesByCompo.set(entry.compo, compoEntries);
        }

        for (const compo of compos.value) {
            const compoEntries = entriesByCompo.get(compo.id) ?? [];

            // Sort by rank (entries without rank go to the end)
            const sorted = [...compoEntries].sort((a, b) => {
                if (a.computed_rank === null && b.computed_rank === null) return 0;
                if (a.computed_rank === null) return 1;
                if (b.computed_rank === null) return -1;
                return a.computed_rank - b.computed_rank;
            });

            // Take top 3 with ranks, excluding disqualified entries
            const top3 = sorted.filter(
                (e) => e.computed_rank !== null && e.computed_rank <= 3 && !e.disqualified
            );

            for (const entry of top3) {
                result.push({
                    author: entry.creator,
                    entryName: entry.name || null,
                    placement: toRomanNumeral(entry.computed_rank!),
                    compoName: compo.name,
                    eventName: eventName.value,
                    hasMultipleAuthors: hasMultipleAuthors(entry.creator),
                    organizers,
                });
            }
        }
    }

    // Process competition participations (if mode includes competitions)
    if (includeCompetitions.value) {
        const participationsByCompetition = new Map<number, CompetitionParticipation[]>();
        for (const participation of participations.value) {
            const compParticipations =
                participationsByCompetition.get(participation.competition) ?? [];
            compParticipations.push(participation);
            participationsByCompetition.set(participation.competition, compParticipations);
        }

        for (const competition of competitions.value) {
            const compParticipations = participationsByCompetition.get(competition.id) ?? [];

            // Sort by rank (participations without rank go to the end)
            const sorted = [...compParticipations].sort((a, b) => {
                if (a.computed_rank === null && b.computed_rank === null) return 0;
                if (a.computed_rank === null) return 1;
                if (b.computed_rank === null) return -1;
                return a.computed_rank - b.computed_rank;
            });

            // Take top 3 with ranks, excluding disqualified participations
            const top3 = sorted.filter(
                (p) => p.computed_rank !== null && p.computed_rank <= 3 && !p.disqualified
            );

            for (const participation of top3) {
                const participantName = participation.participant_name || "Unknown";
                result.push({
                    author: participantName,
                    entryName: null, // No entry for competitions
                    placement: toRomanNumeral(participation.computed_rank!),
                    compoName: competition.name,
                    eventName: eventName.value,
                    hasMultipleAuthors: hasMultipleAuthors(participantName),
                    organizers,
                });
            }
        }
    }

    return result;
});

const noEntriesWarning = computed(
    () => diplomaDataList.value.length === 0 && !loadingUploads.value
);
const canGenerate = computed(
    () => selectedBackground.value !== null && diplomaDataList.value.length > 0 && !generating.value
);

async function loadData() {
    loadingUploads.value = true;
    try {
        // Always load all data - filtering happens in diplomaDataList computed
        const [
            uploadsResponse,
            entriesResponse,
            composResponse,
            competitionsResponse,
            participationsResponse,
        ] = await Promise.all([
            api.adminEventUploadsFilesList({
                path: { event_pk: props.eventId },
                query: { limit: 100 },
            }),
            api.adminEventKompomaattiEntriesList({
                path: { event_pk: props.eventId },
                query: { limit: 10000 },
            }),
            api.adminEventKompomaattiComposList({
                path: { event_pk: props.eventId },
                query: { limit: 100 },
            }),
            api.adminEventKompomaattiCompetitionsList({
                path: { event_pk: props.eventId },
                query: { limit: 100 },
            }),
            api.adminEventKompomaattiCompetitionParticipationsList({
                path: { event_pk: props.eventId },
                query: { limit: 10000 },
            }),
        ]);

        uploads.value = uploadsResponse.data?.results ?? [];
        entries.value = entriesResponse.data?.results ?? [];
        compos.value = composResponse.data?.results ?? [];
        competitions.value = competitionsResponse.data?.results ?? [];
        participations.value = participationsResponse.data?.results ?? [];
    } catch (e) {
        console.error("Failed to load data:", e);
        toast.error(t("DiplomaGenerator.loadFailure"));
    } finally {
        loadingUploads.value = false;
    }
}

function open() {
    loadData();
    dialog.value?.modal();
}

function close() {
    dialog.value?.setResult(false);
    emit("close");
}

function downloadBlob(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

async function generateAll() {
    if (!selectedBackground.value || diplomaDataList.value.length === 0) return;

    generating.value = true;
    progressCurrent.value = 0;
    progressTotal.value = diplomaDataList.value.length;
    try {
        const pdfBytes = await generateAllDiplomasPdf(
            diplomaDataList.value,
            {
                backgroundImageUrl: selectedBackground.value,
            },
            (current, total) => {
                progressCurrent.value = current;
                progressTotal.value = total;
            }
        );
        const blob = new Blob([pdfBytes as BlobPart], { type: "application/pdf" });
        downloadBlob(blob, `diplomas_${eventName.value.replace(/\s+/g, "_")}.pdf`);
        toast.success(t("DiplomaGenerator.success"));
    } catch (e) {
        console.error("Failed to generate diplomas:", e);
        toast.error(t("DiplomaGenerator.generateFailure"));
    } finally {
        generating.value = false;
        progressCurrent.value = 0;
        progressTotal.value = 0;
    }
}

// Reload data when eventId changes
watch(
    () => props.eventId,
    () => {
        if (dialog.value) {
            loadData();
        }
    }
);
</script>
