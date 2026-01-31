<template>
    <LayoutBase :key="`entries-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn v-if="auth.canAdd(PermissionTarget.ENTRY)" @click="createEntry">
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
                <v-text-field
                    v-model="search"
                    variant="outlined"
                    density="compact"
                    :label="t('General.search')"
                    style="max-width: 400px"
                    class="ma-0 pa-0 ml-4"
                    clearable
                />
            </v-row>
        </v-col>
        <v-col>
            <v-row>
                <v-data-table-server
                    :key="`entries-table-${refreshKey}`"
                    v-model:items-per-page="perPage"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="headers"
                    :items="entries"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="search"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('EntriesView.noEntriesFound')"
                    :loading-text="t('EntriesView.loadingEntries')"
                    @update:options="debouncedLoad"
                >
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
                            @edit="editEntry(item.id)"
                            @delete="deleteEntry(item)"
                        />
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, inject, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTableServer, VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { Compo, CompoEntry } from "@/api";
import BooleanIcon from "@/components/table/BooleanIcon.vue";
import ExportButton from "@/components/form/ExportButton.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import TableActionButtons from "@/components/table/TableActionButtons.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";
import { downloadSpreadsheet, type SpreadsheetFormat } from "@/utils/spreadsheet";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{ eventId: string }>();
const { t } = useI18n();
const router = useRouter();
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;
const toast = useToast();
const auth = useAuth();
const { getEventById } = useEvents();
const eventId = computed(() => parseInt(props.eventId, 10));
const loading = ref(false);
const exportLoading = ref(false);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: getEventById(eventId.value)?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    { title: t("EntriesView.title"), disabled: true },
]);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const entries: Ref<CompoEntry[]> = ref([]);
const compos: Ref<Compo[]> = ref([]);
const search = ref("");
const selectedCompo: Ref<number | null> = ref(null);
const refreshKey = ref(0);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const headers: ReadonlyHeaders = [
    {
        title: t("EntriesView.headers.id"),
        sortable: true,
        key: "id",
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
        title: t("EntriesView.headers.compo"),
        sortable: false,
        key: "compo",
    },
    {
        title: t("EntriesView.headers.disqualified"),
        sortable: false,
        key: "disqualified",
    },
    {
        title: t("EntriesView.headers.rank"),
        sortable: true,
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
    refreshKey.value += 1;
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

// Reload when compo filter changes
watch(selectedCompo, () => {
    if (lastLoadArgs.value) {
        debouncedLoad(lastLoadArgs.value);
    }
});

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
            toast.error(t("EntriesView.deleteFailure"));
            console.error(e);
        }
    });
}

function editEntry(id: number): void {
    router.push({ name: "entries-edit", params: { eventId: eventId.value, id } });
}

function createEntry(): void {
    router.push({ name: "entries-new", params: { eventId: eventId.value } });
}

/**
 * Convert a rank number to Roman numerals (1 = I, 2 = II, 3 = III, etc.)
 */
function toRomanNumeral(rank: number): string {
    return "I".repeat(rank);
}

/**
 * Generate spreadsheet data with top 3 entries per compo for diploma generation.
 * Returns array of rows: [Entry Name, Creator, Placement, Compo Name]
 */
function generateResultsData(allEntries: CompoEntry[]): Array<[string, string, string, string]> {
    // Group entries by compo
    const entriesByCompo = new Map<number, CompoEntry[]>();
    for (const entry of allEntries) {
        const compoEntries = entriesByCompo.get(entry.compo) ?? [];
        compoEntries.push(entry);
        entriesByCompo.set(entry.compo, compoEntries);
    }

    // Build rows: top 3 entries per compo, sorted by rank
    const rows: Array<[string, string, string, string]> = [];
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
            rows.push([entry.name, entry.creator, toRomanNumeral(entry.rank), compo.name]);
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
        const data = generateResultsData(response.data!.results);
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
