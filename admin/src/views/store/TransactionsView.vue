<template>
    <LayoutBase :key="`transactions-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-text-field
                    v-model="tableState.search.value"
                    variant="outlined"
                    density="compact"
                    :label="t('General.search')"
                    style="max-width: 400px"
                    class="ma-0 pa-0"
                    clearable
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
                    :items="transactions"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="tableState.search.value"
                    :page="tableState.page.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('TransactionsView.noTransactionsFound')"
                    :loading-text="t('TransactionsView.loadingTransactions')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.time_created="{ item }">
                        <DateTimeCell :value="item.time_created" />
                    </template>
                    <template #item.status="{ item }">
                        <v-chip :color="getStatusColor(item)" size="small" variant="flat">
                            {{ getStatusText(item) }}
                        </v-chip>
                    </template>
                    <template #item.total_price="{ item }">
                        <PriceCell :value="item.total_price" />
                    </template>
                    <template #item.information="{ item }">
                        <LongTextCell
                            :value="item.information"
                            :title="t('TransactionsView.headers.informationDialogTitle')"
                        />
                    </template>
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-view="auth.canView(PermissionTarget.STORE_TRANSACTION)"
                            :can-edit="false"
                            :can-delete="false"
                            @view="viewDetails(item.id)"
                        />
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { StoreTransaction } from "@/api";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import LongTextCell from "@/components/table/LongTextCell.vue";
import PriceCell from "@/components/table/PriceCell.vue";
import TableActionButtons from "@/components/table/TableActionButtons.vue";
import { useTableState } from "@/composables/useTableState";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{ eventId: string }>();
const { t } = useI18n();
const router = useRouter();
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
    { title: t("TransactionsView.title"), disabled: true },
]);

const tableState = useTableState();
const totalItems = ref(0);
const transactions: Ref<StoreTransaction[]> = ref([]);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const headers: ReadonlyHeaders = [
    {
        title: t("TransactionsView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("TransactionsView.headers.fullName"),
        sortable: false,
        key: "full_name",
    },
    {
        title: t("TransactionsView.headers.email"),
        sortable: true,
        key: "email",
    },
    {
        title: t("TransactionsView.headers.created"),
        sortable: true,
        key: "time_created",
    },
    {
        title: t("TransactionsView.headers.status"),
        sortable: false,
        key: "status",
    },
    {
        title: t("TransactionsView.headers.total"),
        sortable: false,
        key: "total_price",
    },
    {
        title: t("TransactionsView.headers.information"),
        sortable: false,
        key: "information",
    },
    {
        title: t("TransactionsView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

function getStatusColor(transaction: StoreTransaction): string {
    if (transaction.is_paid) return "success";
    if (transaction.is_cancelled) return "error";
    if (transaction.is_pending) return "warning";
    return "grey";
}

function getStatusText(transaction: StoreTransaction): string {
    if (transaction.is_paid) return t("TransactionsView.statuses.paid");
    if (transaction.is_cancelled) return t("TransactionsView.statuses.cancelled");
    if (transaction.is_pending) return t("TransactionsView.statuses.pending");
    return t("TransactionsView.statuses.created");
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventStoreTransactionsList({
            path: { event_pk: eventId.value },
            query: getLoadArgs(args),
        });
        transactions.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("TransactionsView.loadFailure"));
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

function refresh() {
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

function viewDetails(id: number): void {
    router.push({ name: "store-transaction-detail", params: { eventId: eventId.value, id } });
}
</script>
