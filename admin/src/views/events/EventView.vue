<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.EVENT)"
                    color="primary"
                    @click="createEvent"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("EventView.newEvent") }}
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
                    v-model="filterArchived"
                    :items="[
                        { title: t('EventView.allEvents'), value: null },
                        { title: t('EventView.archivedOnly'), value: true },
                        { title: t('EventView.notArchivedOnly'), value: false },
                    ]"
                    variant="outlined"
                    density="compact"
                    :label="t('EventView.filterByArchived')"
                    style="max-width: 200px"
                    class="ma-0 pa-0 ml-4"
                />
                <v-select
                    v-model="filterHidden"
                    :items="[
                        { title: t('EventView.allVisibility'), value: null },
                        { title: t('EventView.hiddenOnly'), value: true },
                        { title: t('EventView.visibleOnly'), value: false },
                    ]"
                    variant="outlined"
                    density="compact"
                    :label="t('EventView.filterByVisibility')"
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
                    :items="events"
                    :items-length="totalItems"
                    :loading="loading"
                    :page="tableState.page.value"
                    :search="tableState.search.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('EventView.noEventsFound')"
                    :loading-text="t('EventView.loadingEvents')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.archived="{ item }">
                        <BooleanIcon :value="item.archived" />
                    </template>
                    <template #item.hidden="{ item }">
                        <BooleanIcon :value="item.hidden" />
                    </template>
                    <template #item.date="{ item }">
                        <DateCell :value="item.date" />
                    </template>
                    <template #item.mainurl="{ item }">
                        <a v-if="item.mainurl" :href="item.mainurl" target="_blank">
                            {{ item.mainurl }}
                        </a>
                    </template>
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.EVENT)"
                            :can-delete="auth.canDelete(PermissionTarget.EVENT)"
                            :audit-log="{
                                appLabel: 'kompomaatti',
                                model: 'event',
                                objectPk: item.id,
                            }"
                            @edit="editEvent(item.id)"
                            @delete="deleteEvent(item)"
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
import { debounce } from "lodash-es";
import { type Ref, computed, inject, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { Event } from "@/api";
import BooleanIcon from "@/components/table/BooleanIcon.vue";
import DateCell from "@/components/table/DateCell.vue";
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

const { t } = useI18n();
const router = useRouter();

const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;

const toast = useToast();
const eventService = useEvents();
const auth = useAuth();

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const event = eventService.getLatestEvent();
    return [
        {
            title: event?.name ?? "...",
            to: event ? { name: "dashboard", params: { eventId: event.id } } : undefined,
        },
        { title: t("EventView.title"), disabled: true },
    ];
});

const tableState = useTableState({ filterKeys: ["archived", "hidden"] });
const loading = ref(false);
const totalItems = ref(0);
const events: Ref<Event[]> = ref([]);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const filterArchived = tableState.useBooleanFilter("archived");
const filterHidden = tableState.useBooleanFilter("hidden");
const headers: ReadonlyHeaders = [
    {
        title: t("EventView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("EventView.headers.name"),
        sortable: true,
        key: "name",
    },
    {
        title: t("EventView.headers.tag"),
        sortable: true,
        key: "tag",
    },
    {
        title: t("EventView.headers.date"),
        sortable: true,
        key: "date",
    },
    {
        title: t("EventView.headers.archived"),
        sortable: false,
        key: "archived",
    },
    {
        title: t("EventView.headers.hidden"),
        sortable: false,
        key: "hidden",
    },
    {
        title: t("EventView.headers.mainUrl"),
        sortable: false,
        key: "mainurl",
    },
    {
        title: t("EventView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

async function flushData() {
    if (lastLoadArgs.value) {
        await load(lastLoadArgs.value);
    }
    await eventService.refreshEvents();
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventsList({
            query: {
                ...getLoadArgs(args),
                ...(filterArchived.value !== null ? { archived: filterArchived.value } : {}),
                ...(filterHidden.value !== null ? { hidden: filterHidden.value } : {}),
            },
        });
        events.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("EventView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

// Reload when filters change
watch([filterArchived, filterHidden], () => {
    if (lastLoadArgs.value) {
        debouncedLoad({ ...lastLoadArgs.value, page: 1 });
    }
});

function onTableOptionsUpdate(args: LoadArgs) {
    tableState.onOptionsUpdate(args);
    debouncedLoad(args);
}

async function deleteEvent(item: Event): Promise<void> {
    const text = t("EventView.confirmDelete", item);
    const ok = await confirmDialog.value!.confirm(text);
    if (ok) {
        try {
            await api.adminEventsDestroy({ path: { id: item.id } });
            await flushData();
            toast.success(t("EventView.deleteSuccess"));
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("EventView.deleteFailure")));
            console.error(e);
        }
    }
}

function editEvent(id: number): void {
    router.push({ name: "events-edit", params: { id } });
}

function createEvent(): void {
    router.push({ name: "events-new" });
}
</script>
