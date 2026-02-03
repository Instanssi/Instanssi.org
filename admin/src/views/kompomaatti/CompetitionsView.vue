<template>
    <LayoutBase :key="`competitions-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.COMPETITION)"
                    color="primary"
                    @click="createCompetition"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("CompetitionsView.newCompetition") }}
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
                    v-model="filterActive"
                    :items="[
                        { title: t('CompetitionsView.allStatuses'), value: null },
                        { title: t('CompetitionsView.activeOnly'), value: true },
                        { title: t('CompetitionsView.inactiveOnly'), value: false },
                    ]"
                    variant="outlined"
                    density="compact"
                    :label="t('CompetitionsView.filterByStatus')"
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
                    :items="competitions"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="tableState.search.value"
                    :page="tableState.page.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('CompetitionsView.noCompetitionsFound')"
                    :loading-text="t('CompetitionsView.loadingCompetitions')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.active="{ item }">
                        <BooleanIcon :value="item.active" />
                    </template>
                    <template #item.participation_end="{ item }">
                        <DateTimeCell :value="item.participation_end" />
                    </template>
                    <template #item.start="{ item }">
                        <DateTimeCell :value="item.start" />
                    </template>
                    <template #item.end="{ item }">
                        <DateTimeCell :value="item.end" />
                    </template>
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.COMPETITION)"
                            :can-delete="auth.canDelete(PermissionTarget.COMPETITION)"
                            :audit-log="{
                                appLabel: 'kompomaatti',
                                model: 'competition',
                                objectPk: item.id,
                            }"
                            @edit="editCompetition(item.id)"
                            @delete="deleteCompetition(item)"
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
import { type Ref, computed, inject, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { Competition } from "@/api";
import BooleanIcon from "@/components/table/BooleanIcon.vue";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import TableActionButtons from "@/components/table/TableActionButtons.vue";
import { useTableState } from "@/composables/useTableState";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";
import { getApiErrorMessage } from "@/utils/http";

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

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: getEventById(eventId.value)?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    { title: t("CompetitionsView.title"), disabled: true },
]);

const tableState = useTableState({ filterKeys: ["active"] });
const totalItems = ref(0);
const competitions: Ref<Competition[]> = ref([]);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const filterActive = tableState.useBooleanFilter("active");
const headers: ReadonlyHeaders = [
    {
        title: t("CompetitionsView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("CompetitionsView.headers.name"),
        sortable: true,
        key: "name",
    },
    {
        title: t("CompetitionsView.headers.participationEnd"),
        sortable: true,
        key: "participation_end",
    },
    {
        title: t("CompetitionsView.headers.start"),
        sortable: true,
        key: "start",
    },
    {
        title: t("CompetitionsView.headers.end"),
        sortable: true,
        key: "end",
    },
    {
        title: t("CompetitionsView.headers.active"),
        sortable: true,
        key: "active",
    },
    {
        title: t("CompetitionsView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

function flushData() {
    if (lastLoadArgs.value) {
        load(lastLoadArgs.value);
    }
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventKompomaattiCompetitionsList({
            path: { event_pk: parseInt(props.eventId, 10) },
            query: {
                ...getLoadArgs(args),
                ...(filterActive.value !== null ? { active: filterActive.value } : {}),
            },
        });
        competitions.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("CompetitionsView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

// Reload when filter changes
watch(filterActive, () => {
    if (lastLoadArgs.value) {
        debouncedLoad({ ...lastLoadArgs.value, page: 1 });
    }
});

function onTableOptionsUpdate(args: LoadArgs) {
    tableState.onOptionsUpdate(args);
    debouncedLoad(args);
}

function refresh() {
    tableState.setFilter("active", null);
    tableState.search.value = "";
    tableState.page.value = 1;
    debouncedLoad({
        page: 1,
        itemsPerPage: tableState.perPage.value ?? 25,
        sortBy: [],
        groupBy: [] as never,
        search: "",
    });
}

// Reload when event changes
watch(eventId, refresh);

async function deleteCompetition(item: Competition): Promise<void> {
    const text = t("CompetitionsView.confirmDelete", item);
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventKompomaattiCompetitionsDestroy({
                path: { event_pk: eventId.value, id: item.id },
            });
            toast.success(t("CompetitionsView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("CompetitionsView.deleteFailure")));
            console.error(e);
        }
    });
}

function editCompetition(id: number): void {
    router.push({ name: "competitions-edit", params: { eventId: eventId.value, id } });
}

function createCompetition(): void {
    router.push({ name: "competitions-new", params: { eventId: eventId.value } });
}
</script>
