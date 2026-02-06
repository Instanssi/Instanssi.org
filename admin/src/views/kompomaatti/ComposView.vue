<template>
    <LayoutBase :key="`compos-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.COMPO)"
                    color="primary"
                    @click="createCompo"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("ComposView.newCompo") }}
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
                        { title: t('ComposView.allStatuses'), value: null },
                        { title: t('ComposView.activeOnly'), value: true },
                        { title: t('ComposView.inactiveOnly'), value: false },
                    ]"
                    variant="outlined"
                    density="compact"
                    :label="t('ComposView.filterByStatus')"
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
                    :items="compos"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="tableState.search.value"
                    :page="tableState.page.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('ComposView.noComposFound')"
                    :loading-text="t('ComposView.loadingCompos')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.active="{ item }">
                        <BooleanIcon :value="item.active" />
                    </template>
                    <template #item.adding_end="{ item }">
                        <DateTimeCell :value="item.adding_end" />
                    </template>
                    <template #item.voting_start="{ item }">
                        <DateTimeCell :value="item.voting_start" />
                    </template>
                    <template #item.voting_end="{ item }">
                        <DateTimeCell :value="item.voting_end" />
                    </template>
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.COMPO)"
                            :can-delete="auth.canDelete(PermissionTarget.COMPO)"
                            :audit-log="{
                                appLabel: 'kompomaatti',
                                model: 'compo',
                                objectPk: item.id,
                            }"
                            @edit="editCompo(item.id)"
                            @delete="deleteCompo(item)"
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
import { useRoute, useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { Compo } from "@/api";
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
const route = useRoute();
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
    { title: t("ComposView.title"), disabled: true },
]);

const tableState = useTableState({
    filterKeys: ["active"],
    initialSort: { key: "id", order: "desc" },
});
const totalItems = ref(0);
const compos: Ref<Compo[]> = ref([]);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const filterActive = tableState.useBooleanFilter("active");
const headers: ReadonlyHeaders = [
    {
        title: t("ComposView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("ComposView.headers.name"),
        sortable: true,
        key: "name",
    },
    {
        title: t("ComposView.headers.addingEnd"),
        sortable: true,
        key: "adding_end",
    },
    {
        title: t("ComposView.headers.votingStart"),
        sortable: true,
        key: "voting_start",
    },
    {
        title: t("ComposView.headers.votingEnd"),
        sortable: true,
        key: "voting_end",
    },
    {
        title: t("ComposView.headers.active"),
        sortable: true,
        key: "active",
    },
    {
        title: t("ComposView.headers.actions"),
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
        const response = await api.adminEventKompomaattiComposList({
            path: { event_pk: parseInt(props.eventId, 10) },
            query: {
                ...getLoadArgs(args),
                ...(filterActive.value !== null ? { active: filterActive.value } : {}),
            },
        });
        compos.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("ComposView.loadFailure"));
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

async function deleteCompo(item: Compo): Promise<void> {
    const text = t("ComposView.confirmDelete", item);
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventKompomaattiComposDestroy({
                path: { event_pk: eventId.value, id: item.id },
            });
            toast.success(t("ComposView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("ComposView.deleteFailure")));
            console.error(e);
        }
    });
}

function editCompo(id: number): void {
    router.push({
        name: "compos-edit",
        params: { eventId: eventId.value, id },
        query: route.query,
    });
}

function createCompo(): void {
    router.push({ name: "compos-new", params: { eventId: eventId.value }, query: route.query });
}
</script>
