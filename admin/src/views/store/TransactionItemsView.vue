<template>
    <LayoutBase :key="`transaction-items-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <ExportButton
                    :label="t('TransactionItemsView.export')"
                    :loading="exportLoading"
                    @export="exportData"
                />
                <v-select
                    v-model="selectedItem"
                    :items="itemOptions"
                    variant="outlined"
                    density="compact"
                    :label="t('TransactionItemsView.filterByItem')"
                    style="max-width: 300px"
                    class="ma-0 pa-0 ml-4"
                    clearable
                />
                <v-text-field
                    v-model="tableState.search.value"
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
                    v-model:items-per-page="tableState.perPage.value"
                    :sort-by="tableState.sortByArray.value"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="headers"
                    :items="items"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="tableState.search.value"
                    :page="tableState.page.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('TransactionItemsView.noItemsFound')"
                    :loading-text="t('TransactionItemsView.loadingItems')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.item="{ item }">
                        {{ getItemName(item.item) }}
                    </template>
                    <template #item.variant="{ item }">
                        {{ getVariantName(item.item, item.variant) }}
                    </template>
                    <template #item.purchase_price="{ item }">
                        <PriceCell :value="item.purchase_price" />
                    </template>
                    <template #item.is_delivered="{ item }">
                        <BooleanIcon :value="item.is_delivered" />
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { TransactionItem, StoreItem, StoreTransaction } from "@/api";
import BooleanIcon from "@/components/table/BooleanIcon.vue";
import ExportButton from "@/components/form/ExportButton.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import PriceCell from "@/components/table/PriceCell.vue";
import { useTableState } from "@/composables/useTableState";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { downloadSpreadsheet, type SpreadsheetFormat } from "@/utils/spreadsheet";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{ eventId: string }>();
const { t } = useI18n();
const toast = useToast();
const { getEventById } = useEvents();
const eventId = computed(() => parseInt(props.eventId, 10));
const loading = ref(false);
const exportLoading = ref(false);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: getEventById(eventId.value)?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    { title: t("TransactionItemsView.title"), disabled: true },
]);

const tableState = useTableState({ filterKeys: ["item"] });
const totalItems = ref(0);
const items: Ref<TransactionItem[]> = ref([]);
const storeItems: Ref<StoreItem[]> = ref([]);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const selectedItem = computed({
    get: () => tableState.getFilterAsNumber("item"),
    set: (value: number | null) => {
        tableState.setFilter("item", value);
        tableState.resetPage();
    },
});

const headers: ReadonlyHeaders = [
    {
        title: t("TransactionItemsView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("TransactionItemsView.headers.transactionId"),
        sortable: true,
        key: "transaction",
    },
    {
        title: t("TransactionItemsView.headers.item"),
        sortable: true,
        key: "item",
    },
    {
        title: t("TransactionItemsView.headers.variant"),
        sortable: false,
        key: "variant",
    },
    {
        title: t("TransactionItemsView.headers.price"),
        sortable: true,
        key: "purchase_price",
    },
    {
        title: t("TransactionItemsView.headers.key"),
        sortable: false,
        key: "key",
    },
    {
        title: t("TransactionItemsView.headers.delivered"),
        sortable: false,
        key: "is_delivered",
    },
];

const itemOptions = computed(() => [
    { title: t("TransactionItemsView.allItems"), value: null },
    ...storeItems.value.map((item) => ({ title: item.name, value: item.id })),
]);

function getItemName(itemId: number): string {
    const item = storeItems.value.find((i) => i.id === itemId);
    return item?.name ?? `#${itemId}`;
}

function getVariantName(itemId: number, variantId: number | null | undefined): string {
    if (!variantId) return "-";
    const item = storeItems.value.find((i) => i.id === itemId);
    if (!item) return `#${variantId}`;
    const variant = item.variants?.find((v) => v.id === variantId);
    return variant?.name ?? `#${variantId}`;
}

async function loadStoreItems() {
    try {
        const response = await api.adminEventStoreItemsList({
            path: { event_pk: eventId.value },
            query: { limit: 1000 },
        });
        storeItems.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load store items:", e);
    }
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventStoreTransactionItemsList({
            path: { event_pk: eventId.value },
            query: {
                ...getLoadArgs(args),
                ...(selectedItem.value ? { item: selectedItem.value } : {}),
            },
        });
        items.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("TransactionItemsView.loadFailure"));
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

// Reload when item filter changes
watch(selectedItem, () => {
    if (lastLoadArgs.value) {
        debouncedLoad({ ...lastLoadArgs.value, page: 1 });
    }
});

function refresh() {
    selectedItem.value = null;
    tableState.search.value = "";
    tableState.page.value = 1;
    loadStoreItems();
    debouncedLoad({
        page: 1,
        itemsPerPage: tableState.perPage.value ?? 25,
        sortBy: [],
        groupBy: [] as never,
        search: "",
    });
}

// Reload store items when event changes
watch(eventId, refresh);

async function exportData(format: SpreadsheetFormat): Promise<void> {
    exportLoading.value = true;
    try {
        // Fetch all data for export
        const [itemsResponse, transactionsResponse, txItemsResponse] = await Promise.all([
            api.adminEventStoreItemsList({
                path: { event_pk: eventId.value },
                query: { limit: 1000 },
            }),
            api.adminEventStoreTransactionsList({
                path: { event_pk: eventId.value },
                query: { limit: 10000 },
            }),
            api.adminEventStoreTransactionItemsList({
                path: { event_pk: eventId.value },
                query: { limit: 10000 },
            }),
        ]);

        const allStoreItems = itemsResponse.data!.results;
        const transactions = transactionsResponse.data!.results;
        const txItems = txItemsResponse.data!.results;

        // Build transaction lookup map
        const transactionMap = new Map<number, StoreTransaction>();
        for (const tx of transactions) {
            transactionMap.set(tx.id, tx);
        }

        // Helper to get item/variant names
        const getExportItemName = (itemId: number): string => {
            const item = allStoreItems.find((i) => i.id === itemId);
            return item?.name ?? `#${itemId}`;
        };
        const getExportVariantName = (
            itemId: number,
            variantId: number | null | undefined
        ): string => {
            if (!variantId) return "";
            const item = allStoreItems.find((i) => i.id === itemId);
            if (!item) return `#${variantId}`;
            const variant = item.variants?.find((v) => v.id === variantId);
            return variant?.name ?? `#${variantId}`;
        };

        // Build export data with headers
        const data: Array<Array<string | number>> = [
            [
                "Item ID",
                "Product",
                "Variant",
                "Purchase Price",
                "Original Price",
                "Delivered",
                "Delivery Time",
                "Transaction ID",
                "First Name",
                "Last Name",
                "Company",
                "Email",
                "Telephone",
                "Mobile",
                "Street",
                "Postal Code",
                "City",
                "Country",
                "Status",
                "Created",
                "Paid",
                "Total Price",
            ],
        ];

        for (const txItem of txItems) {
            const tx = transactionMap.get(txItem.transaction);
            const status = tx?.is_paid
                ? "Paid"
                : tx?.is_cancelled
                  ? "Cancelled"
                  : tx?.is_pending
                    ? "Pending"
                    : "Created";

            data.push([
                txItem.id,
                getExportItemName(txItem.item),
                getExportVariantName(txItem.item, txItem.variant),
                txItem.purchase_price,
                txItem.original_price,
                txItem.is_delivered ? "Yes" : "No",
                txItem.time_delivered ?? "",
                tx?.id ?? "",
                tx?.firstname ?? "",
                tx?.lastname ?? "",
                tx?.company ?? "",
                tx?.email ?? "",
                tx?.telephone ?? "",
                tx?.mobile ?? "",
                tx?.street ?? "",
                tx?.postalcode ?? "",
                tx?.city ?? "",
                tx?.country ?? "",
                status,
                tx?.time_created ?? "",
                tx?.time_paid ?? "",
                tx?.total_price ?? "",
            ]);
        }

        downloadSpreadsheet(data, "instanssi_transaction_items", format, "Transaction Items");
        toast.success(t("TransactionItemsView.exportSuccess"));
    } catch (e) {
        toast.error(t("TransactionItemsView.exportFailure"));
        console.error(e);
    } finally {
        exportLoading.value = false;
    }
}

onMounted(() => {
    loadStoreItems();
});
</script>
