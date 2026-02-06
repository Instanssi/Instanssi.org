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
import type { UploadedFile } from "@/api";
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
const compoDiplomas: Ref<DiplomaData[]> = ref([]);
const competitionDiplomas: Ref<DiplomaData[]> = ref([]);

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

const diplomaDataList = computed<DiplomaData[]>(() => [
    ...(includeCompos.value ? compoDiplomas.value : []),
    ...(includeCompetitions.value ? competitionDiplomas.value : []),
]);

const noEntriesWarning = computed(
    () => diplomaDataList.value.length === 0 && !loadingUploads.value
);
const canGenerate = computed(
    () => selectedBackground.value !== null && diplomaDataList.value.length > 0 && !generating.value
);

/**
 * Take items whose rank is among the first 3 distinct ranks.
 * Assumes items are already sorted by rank ascending from the backend.
 */
function takeTop3Ranks<T extends { computed_rank: number | null }>(items: T[]): T[] {
    const ranks = new Set<number>();
    const result: T[] = [];
    for (const item of items) {
        if (item.computed_rank === null) continue;
        ranks.add(item.computed_rank);
        if (ranks.size > 3) break;
        result.push(item);
    }
    return result;
}

function getOrganizers(): DiplomaOrganizers {
    return {
        mainOrganizer: { name: mainOrganizerName.value, title: mainOrganizerTitle.value },
        programOrganizer: { name: programOrganizerName.value, title: programOrganizerTitle.value },
    };
}

async function loadCompoDiplomas(
    compos: { id: number; name: string }[],
    name: string,
    organizers: DiplomaOrganizers
): Promise<DiplomaData[]> {
    const responses = await Promise.all(
        compos.map((compo) =>
            api.adminEventKompomaattiEntriesList({
                path: { event_pk: props.eventId },
                query: {
                    compo: compo.id,
                    disqualified: false,
                    ordering: "computed_rank",
                    limit: 100,
                },
            })
        )
    );
    return compos.flatMap((compo, i) => {
        const entries = takeTop3Ranks(responses[i]?.data?.results ?? []);
        return entries.map((entry) => ({
            author: entry.creator,
            entryName: entry.name || null,
            placement: toRomanNumeral(entry.computed_rank!),
            compoName: compo.name,
            eventName: name,
            hasMultipleAuthors: hasMultipleAuthors(entry.creator),
            organizers,
        }));
    });
}

async function loadCompetitionDiplomas(
    competitions: { id: number; name: string }[],
    name: string,
    organizers: DiplomaOrganizers
): Promise<DiplomaData[]> {
    const responses = await Promise.all(
        competitions.map((competition) =>
            api.adminEventKompomaattiCompetitionParticipationsList({
                path: { event_pk: props.eventId },
                query: {
                    competition: competition.id,
                    disqualified: false,
                    ordering: "computed_rank",
                    limit: 100,
                },
            })
        )
    );
    return competitions.flatMap((competition, i) => {
        const participations = takeTop3Ranks(responses[i]?.data?.results ?? []);
        return participations.map((p) => {
            const participantName = p.participant_name || "Unknown";
            return {
                author: participantName,
                entryName: null,
                placement: toRomanNumeral(p.computed_rank!),
                compoName: competition.name,
                eventName: name,
                hasMultipleAuthors: hasMultipleAuthors(participantName),
                organizers,
            };
        });
    });
}

async function loadData() {
    loadingUploads.value = true;
    try {
        const [uploadsResponse, composResponse, competitionsResponse] = await Promise.all([
            api.adminEventUploadsFilesList({
                path: { event_pk: props.eventId },
                query: { limit: 100 },
            }),
            api.adminEventKompomaattiComposList({
                path: { event_pk: props.eventId },
                query: { limit: 100 },
            }),
            api.adminEventKompomaattiCompetitionsList({
                path: { event_pk: props.eventId },
                query: { limit: 100 },
            }),
        ]);

        uploads.value = uploadsResponse.data?.results ?? [];
        const compos = composResponse.data?.results ?? [];
        const competitions = competitionsResponse.data?.results ?? [];
        const name = eventName.value;
        const organizers = getOrganizers();

        [compoDiplomas.value, competitionDiplomas.value] = await Promise.all([
            loadCompoDiplomas(compos, name, organizers),
            loadCompetitionDiplomas(competitions, name, organizers),
        ]);
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
