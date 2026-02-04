<template>
    <LayoutBase :key="`entries-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.ENTRY)"
                    color="primary"
                    @click="createEntry"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("EntriesView.newEntry") }}
                </v-btn>
                <div v-if="auth.canView(PermissionTarget.ENTRY)" class="ml-4">
                    <ExportButton
                        :label="t('EntriesView.exportResults')"
                        :loading="exportLoading"
                        @export="downloadResults"
                    />
                </div>
                <v-btn
                    v-if="auth.canView(PermissionTarget.ENTRY)"
                    color="secondary"
                    class="ml-4"
                    @click="openDiplomaDialog"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="faCertificate" />
                    </template>
                    {{ t("DiplomaGenerator.title") }}
                </v-btn>
                <v-text-field
                    v-model="tableState.search.value"
                    variant="outlined"
                    density="compact"
                    :label="t('General.search')"
                    style="max-width: 400px"
                    class="ma-0 pa-0 ml-4"
                    clearable
                />
                <v-select
                    v-model="selectedCompo"
                    :items="compoOptions"
                    variant="outlined"
                    density="compact"
                    :label="t('EntriesView.filterByCompo')"
                    style="max-width: 300px"
                    class="ma-0 pa-0 ml-4"
                    clearable
                />
                <v-select
                    v-model="filterDisqualified"
                    :items="[
                        { title: t('EntriesView.allStatuses'), value: null },
                        { title: t('General.disqualifiedOn'), value: true },
                        { title: t('General.disqualifiedOff'), value: false },
                    ]"
                    variant="outlined"
                    density="compact"
                    :label="t('EntriesView.filterByDisqualified')"
                    style="max-width: 200px"
                    class="ma-0 pa-0 ml-4"
                />
            </v-row>
        </v-col>
        <v-col>
            <v-row>
                <v-data-table-server
                    v-model:items-per-page="tableState.perPage.value"
                    :sort-by="tableState.sortByArray.value"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="headers"
                    :items="entries"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="tableState.search.value"
                    :page="tableState.page.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('EntriesView.noEntriesFound')"
                    :loading-text="t('EntriesView.loadingEntries')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.imagefile_thumbnail_url="{ item }">
                        <ImageCell :url="item.imagefile_thumbnail_url" />
                    </template>
                    <template #item.entryfile_url="{ item }">
                        <MediaCell :url="item.entryfile_url" />
                    </template>
                    <template #item.disqualified="{ item }">
                        <BooleanIcon
                            :value="item.disqualified"
                            true-class="text-red"
                            false-class="text-green"
                        />
                    </template>
                    <template #item.compo="{ item }">
                        {{ getCompoName(item.compo) }}
                    </template>
                    <template #item.rank="{ item }">
                        {{ item.rank ?? "-" }}
                    </template>
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.ENTRY)"
                            :can-delete="auth.canDelete(PermissionTarget.ENTRY)"
                            :audit-log="{
                                appLabel: 'kompomaatti',
                                model: 'entry',
                                objectPk: item.id,
                            }"
                            @edit="editEntry(item.id)"
                            @delete="deleteEntry(item)"
                        />
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
        <DiplomaGeneratorDialog ref="diplomaDialog" :event-id="eventId" />
    </LayoutBase>
</template>

<script setup lang="ts">
import { faCertificate, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, inject, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { Compo, CompoEntry } from "@/api";
import BooleanIcon from "@/components/table/BooleanIcon.vue";
import ExportButton from "@/components/form/ExportButton.vue";
import ImageCell from "@/components/table/ImageCell.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import MediaCell from "@/components/table/MediaCell.vue";
import TableActionButtons from "@/components/table/TableActionButtons.vue";
import { useTableState } from "@/composables/useTableState";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";
import { toRomanNumeral } from "@/utils/roman";
import { getApiErrorMessage } from "@/utils/http";
import { downloadSpreadsheet, type SpreadsheetFormat } from "@/utils/spreadsheet";
import DiplomaGeneratorDialog from "./DiplomaGeneratorDialog.vue";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{ eventId: string }>();
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;
const toast = useToast();
const auth = useAuth();
const { getEventById } = useEvents();
const eventId = computed(() => parseInt(props.eventId, 10));
const loading = ref(false);
const exportLoading = ref(false);
const diplomaDialog: Ref<InstanceType<typeof DiplomaGeneratorDialog> | undefined> = ref(undefined);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: getEventById(eventId.value)?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    { title: t("EntriesView.title"), disabled: true },
]);

const tableState = useTableState({
    filterKeys: ["compo", "disqualified"],
    defaultSort: { key: "id", order: "desc" },
});
const totalItems = ref(0);
const entries: Ref<CompoEntry[]> = ref([]);
const compos: Ref<Compo[]> = ref([]);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const selectedCompo = computed({
    get: () => tableState.getFilterAsNumber("compo"),
    set: (value: number | null) => {
        tableState.setFilter("compo", value);
        tableState.resetPage();
    },
});

const filterDisqualified = tableState.useBooleanFilter("disqualified");

const headers: ReadonlyHeaders = [
    {
        title: t("EntriesView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("EntriesView.headers.image"),
        sortable: false,
        key: "imagefile_thumbnail_url",
        width: 60,
    },
    {
        title: t("EntriesView.headers.name"),
        sortable: true,
        key: "name",
    },
    {
        title: t("EntriesView.headers.creator"),
        sortable: true,
        key: "creator",
    },
    {
        title: t("EntriesView.headers.entryfile"),
        sortable: false,
        key: "entryfile_url",
    },
    {
        title: t("EntriesView.headers.compo"),
        sortable: true,
        key: "compo",
    },
    {
        title: t("EntriesView.headers.disqualified"),
        sortable: false,
        key: "disqualified",
    },
    {
        title: t("EntriesView.headers.rank"),
        sortable: false,
        key: "rank",
    },
    {
        title: t("EntriesView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

const compoOptions = computed(() => [
    { title: t("EntriesView.allCompos"), value: null },
    ...compos.value.map((c) => ({ title: c.name, value: c.id })),
]);

function getCompoName(compoId: number): string {
    const compo = compos.value.find((c) => c.id === compoId);
    return compo?.name ?? `#${compoId}`;
}

function flushData() {
    if (lastLoadArgs.value) {
        load(lastLoadArgs.value);
    }
}

async function loadCompos() {
    try {
        const response = await api.adminEventKompomaattiComposList({
            path: { event_pk: eventId.value },
            query: { limit: 100 },
        });
        compos.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load compos:", e);
    }
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventKompomaattiEntriesList({
            path: { event_pk: parseInt(props.eventId, 10) },
            query: {
                ...getLoadArgs(args),
                ...(selectedCompo.value ? { compo: selectedCompo.value } : {}),
                ...(filterDisqualified.value !== null
                    ? { disqualified: filterDisqualified.value }
                    : {}),
            },
        });
        entries.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("EntriesView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

function onTableOptionsUpdate(args: LoadArgs) {
    tableState.onOptionsUpdate(args);
    debouncedLoad(args);
}

// Reload when filters change
watch([selectedCompo, filterDisqualified], () => {
    if (lastLoadArgs.value) {
        debouncedLoad({ ...lastLoadArgs.value, page: 1 });
    }
});

function refresh() {
    tableState.setFilter("compo", null);
    tableState.setFilter("disqualified", null);
    tableState.search.value = "";
    tableState.page.value = 1;
    loadCompos();
    debouncedLoad({
        page: 1,
        itemsPerPage: tableState.perPage.value ?? 25,
        sortBy: [],
        groupBy: [] as never,
        search: "",
    });
}

// Reload compos and entries when event changes
watch(eventId, refresh);

async function deleteEntry(item: CompoEntry): Promise<void> {
    const text = t("EntriesView.confirmDelete", item);
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventKompomaattiEntriesDestroy({
                path: { event_pk: eventId.value, id: item.id },
            });
            toast.success(t("EntriesView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("EntriesView.deleteFailure")));
            console.error(e);
        }
    });
}

function editEntry(id: number): void {
    router.push({
        name: "entries-edit",
        params: { eventId: eventId.value, id },
        query: route.query,
    });
}

function createEntry(): void {
    router.push({ name: "entries-new", params: { eventId: eventId.value }, query: route.query });
}

function openDiplomaDialog(): void {
    diplomaDialog.value?.open();
}

interface ResultRow {
    entryName: string;
    creator: string;
    rankString: string;
    compoName: string;
}

/**
 * Generate results data with top 3 entries per compo for diploma generation.
 */
function generateResultsData(allEntries: CompoEntry[]): ResultRow[] {
    // Group entries by compo
    const entriesByCompo = new Map<number, CompoEntry[]>();
    for (const entry of allEntries) {
        const compoEntries = entriesByCompo.get(entry.compo) ?? [];
        compoEntries.push(entry);
        entriesByCompo.set(entry.compo, compoEntries);
    }

    // Build rows: top 3 entries per compo, sorted by rank
    const rows: ResultRow[] = [];
    for (const compo of compos.value) {
        const compoEntries = entriesByCompo.get(compo.id) ?? [];

        // Sort by rank (entries without rank go to the end)
        const sorted = [...compoEntries].sort((a, b) => {
            if (a.rank === null && b.rank === null) return 0;
            if (a.rank === null) return 1;
            if (b.rank === null) return -1;
            return a.rank - b.rank;
        });

        // Take top 3
        const top3 = sorted.slice(0, 3);

        for (const entry of top3) {
            if (entry.rank === null) continue; // Skip unranked entries
            rows.push({
                entryName: entry.name,
                creator: entry.creator,
                rankString: toRomanNumeral(entry.rank),
                compoName: compo.name,
            });
        }
    }

    return rows;
}

/**
 * Generate and download spreadsheet with top 3 entries per compo for diploma generation
 */
async function downloadResults(format: SpreadsheetFormat): Promise<void> {
    exportLoading.value = true;
    try {
        const response = await api.adminEventKompomaattiEntriesList({
            path: { event_pk: eventId.value },
            query: { limit: 10000 },
        });
        const results = generateResultsData(response.data!.results);
        const data = results.map((row) => [
            row.entryName,
            row.creator,
            row.rankString,
            row.compoName,
        ]);
        downloadSpreadsheet(data, "instanssi_entries", format, "Results");
        toast.success(t("EntriesView.exportSuccess"));
    } catch (e) {
        toast.error(t("EntriesView.exportFailure"));
        console.error(e);
    } finally {
        exportLoading.value = false;
    }
}

onMounted(() => {
    loadCompos();
});
</script>
