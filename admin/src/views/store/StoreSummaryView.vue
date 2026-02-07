<template>
    <LayoutBase :key="`store-summary-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <!-- Summary Cards -->
            <v-row>
                <v-col cols="12" sm="6">
                    <StatCard
                        :icon="faBoxOpen"
                        :value="totalItemsSold"
                        :label="t('StoreSummaryView.totals.totalItems')"
                        color="primary"
                    />
                </v-col>
                <v-col cols="12" sm="6">
                    <StatCard
                        :icon="faEuroSign"
                        :value="`${totalRevenue.toFixed(2)} €`"
                        :label="t('StoreSummaryView.totals.totalRevenue')"
                        color="success"
                    />
                </v-col>
            </v-row>

            <!-- Charts -->
            <v-row class="mt-2">
                <v-col cols="12" md="6">
                    <SalesPerDayChart :paid-times="paidTimesForItems" />
                </v-col>
                <v-col cols="12" md="6">
                    <SalesByHourChart :paid-times="paidTimesForItems" />
                </v-col>
            </v-row>

            <!-- Sales Table -->
            <v-row class="mt-2">
                <v-col cols="12">
                    <v-card>
                        <v-card-title class="d-flex align-center">
                            {{ t("StoreSummaryView.title") }}
                            <v-spacer />
                            <ExportButton
                                :label="t('StoreSummaryView.export')"
                                :loading="exportLoading"
                                size="small"
                                @export="exportData"
                            />
                        </v-card-title>
                        <v-card-text>
                            <v-data-table
                                v-if="summaryRows.length > 0"
                                :headers="headers"
                                :items="summaryRows"
                                density="compact"
                                class="elevation-0"
                                :items-per-page="-1"
                                hide-default-footer
                            >
                                <template #item.revenue="{ item }">
                                    {{ item.revenue.toFixed(2) }} &euro;
                                </template>
                            </v-data-table>
                            <div v-else class="text-grey text-center py-8">
                                {{ t("StoreSummaryView.noSalesFound") }}
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </v-col>

        <RefreshControl @refresh="loadData" />
    </LayoutBase>
</template>

<script setup lang="ts">
import { faBoxOpen, faEuroSign } from "@fortawesome/free-solid-svg-icons";
import { parseInt } from "lodash-es";
import { computed, ref, type Ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import { Temporal } from "temporal-polyfill";

import * as api from "@/api";
import type { StoreItem, StoreTransaction, TransactionItem } from "@/api";
import RefreshControl from "@/components/dashboard/RefreshControl.vue";
import SalesByHourChart from "@/components/dashboard/charts/SalesByHourChart.vue";
import SalesPerDayChart from "@/components/dashboard/charts/SalesPerDayChart.vue";
import ExportButton from "@/components/form/ExportButton.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import StatCard from "@/components/dashboard/StatCard.vue";
import { useEvents } from "@/services/events";
import { ADMIN_TIMEZONE } from "@/utils/datetime";
import { useAsyncAction } from "@/composables/useAsyncAction";
import { downloadSpreadsheet, type SpreadsheetFormat } from "@/utils/spreadsheet";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

interface SummaryRow {
    item: string;
    variant: string;
    quantity: number;
    revenue: number;
}

const props = defineProps<{ eventId: string }>();
const { t } = useI18n();
const toast = useToast();
const { getEventById } = useEvents();
const eventId = computed(() => parseInt(props.eventId, 10));
const { loading: exportLoading, run: runExport } = useAsyncAction({
    successMessage: t("StoreSummaryView.exportSuccess"),
    failureMessage: t("StoreSummaryView.exportFailure"),
});

const storeItems: Ref<StoreItem[]> = ref([]);
const transactions: Ref<StoreTransaction[]> = ref([]);
const transactionItems: Ref<TransactionItem[]> = ref([]);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: getEventById(eventId.value)?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    { title: t("StoreSummaryView.title"), disabled: true },
]);

const headers: ReadonlyHeaders = [
    {
        title: t("StoreSummaryView.headers.item"),
        key: "item",
        sortable: true,
    },
    {
        title: t("StoreSummaryView.headers.variant"),
        key: "variant",
        sortable: true,
    },
    {
        title: t("StoreSummaryView.headers.quantity"),
        key: "quantity",
        sortable: true,
        align: "end",
    },
    {
        title: t("StoreSummaryView.headers.revenue"),
        key: "revenue",
        sortable: true,
        align: "end",
    },
];

// Get paid transactions sorted by time
const paidTransactions = computed(() => {
    return transactions.value
        .filter((tx) => tx.is_paid && tx.time_paid)
        .sort((a, b) => {
            const timeA = a.time_paid ? new Date(a.time_paid).getTime() : 0;
            const timeB = b.time_paid ? new Date(b.time_paid).getTime() : 0;
            return timeA - timeB;
        });
});

// Get set of paid transaction IDs
const paidTransactionIds = computed(() => {
    return new Set(paidTransactions.value.map((t) => t.id));
});

// Filter transaction items to only include paid ones
const paidTransactionItems = computed(() => {
    return transactionItems.value.filter((item) => paidTransactionIds.value.has(item.transaction));
});

// Build transaction ID to paid time map (in Helsinki timezone)
const transactionPaidTimeMap = computed(() => {
    const map = new Map<number, Temporal.ZonedDateTime>();
    for (const tx of paidTransactions.value) {
        if (tx.time_paid) {
            const instant = Temporal.Instant.from(tx.time_paid);
            map.set(tx.id, instant.toZonedDateTimeISO(ADMIN_TIMEZONE));
        }
    }
    return map;
});

// Get paid times array for charts (one entry per transaction item)
const paidTimesForItems = computed(() => {
    const times: Temporal.ZonedDateTime[] = [];
    for (const txItem of paidTransactionItems.value) {
        const paidTime = transactionPaidTimeMap.value.get(txItem.transaction);
        if (paidTime) {
            times.push(paidTime);
        }
    }
    return times;
});

// Build summary rows grouped by item + variant
const summaryRows = computed<SummaryRow[]>(() => {
    const grouped = new Map<string, SummaryRow>();

    for (const txItem of paidTransactionItems.value) {
        const itemName = getItemName(txItem.item);
        const variantName = getVariantName(txItem.item, txItem.variant);
        const key = `${txItem.item}-${txItem.variant ?? "null"}`;

        if (!grouped.has(key)) {
            grouped.set(key, {
                item: itemName,
                variant: variantName,
                quantity: 0,
                revenue: 0,
            });
        }

        const row = grouped.get(key)!;
        row.quantity += 1;
        row.revenue += parseFloat(txItem.purchase_price);
    }

    return Array.from(grouped.values()).sort((a, b) => a.item.localeCompare(b.item));
});

const totalItemsSold = computed(() => {
    return summaryRows.value.reduce((sum, row) => sum + row.quantity, 0);
});

const totalRevenue = computed(() => {
    return summaryRows.value.reduce((sum, row) => sum + row.revenue, 0);
});

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

async function loadData() {
    try {
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
        storeItems.value = itemsResponse.data!.results;
        transactions.value = transactionsResponse.data!.results;
        transactionItems.value = txItemsResponse.data!.results;
    } catch (e) {
        toast.error(t("StoreSummaryView.loadFailure"));
        console.error(e);
    }
}

function exportData(format: SpreadsheetFormat): void {
    runExport(() => {
        const data: Array<Array<string | number>> = [
            ["Item", "Variant", "Quantity Sold", "Revenue (EUR)"],
        ];

        for (const row of summaryRows.value) {
            data.push([row.item, row.variant, row.quantity, row.revenue.toFixed(2)]);
        }

        // Add totals row
        data.push([]);
        data.push(["TOTAL", "", totalItemsSold.value, totalRevenue.value.toFixed(2)]);

        downloadSpreadsheet(data, "instanssi_sales_summary", format, "Sales Summary");
    });
}
</script>
