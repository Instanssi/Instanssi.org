<template>
    <LayoutBase :key="`store-summary-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <!-- Summary Cards -->
            <v-row class="mb-4">
                <v-col cols="12" sm="6">
                    <v-card color="primary" variant="tonal">
                        <v-card-text class="d-flex align-center">
                            <FontAwesomeIcon :icon="faBoxOpen" size="2x" class="mr-4" />
                            <div>
                                <div class="text-h4">{{ totalItemsSold }}</div>
                                <div class="text-body-2">
                                    {{ t("StoreSummaryView.totals.totalItems") }}
                                </div>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col cols="12" sm="6">
                    <v-card color="success" variant="tonal">
                        <v-card-text class="d-flex align-center">
                            <FontAwesomeIcon :icon="faEuroSign" size="2x" class="mr-4" />
                            <div>
                                <div class="text-h4">{{ totalRevenue.toFixed(2) }} &euro;</div>
                                <div class="text-body-2">
                                    {{ t("StoreSummaryView.totals.totalRevenue") }}
                                </div>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Charts -->
            <v-row class="mb-4">
                <v-col cols="12" md="6">
                    <v-card>
                        <v-card-title>
                            {{ t("StoreSummaryView.charts.salesPerDay") }}
                        </v-card-title>
                        <v-card-text>
                            <div v-if="salesPerDayData.labels.length > 0" style="height: 300px">
                                <Bar :data="salesPerDayData" :options="barChartOptions" />
                            </div>
                            <div v-else class="text-center text-grey py-8">
                                {{ t("StoreSummaryView.charts.noData") }}
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col cols="12" md="6">
                    <v-card>
                        <v-card-title>
                            {{ t("StoreSummaryView.charts.salesByHour") }}
                        </v-card-title>
                        <v-card-text>
                            <div v-if="salesByHourData.labels.length > 0" style="height: 300px">
                                <Bar :data="salesByHourData" :options="barChartOptions" />
                            </div>
                            <div v-else class="text-center text-grey py-8">
                                {{ t("StoreSummaryView.charts.noData") }}
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Sales Table -->
            <v-row>
                <v-col cols="12">
                    <v-card>
                        <v-card-title class="d-flex align-center">
                            {{ t("StoreSummaryView.title") }}
                            <v-spacer />
                            <v-menu>
                                <template #activator="{ props: menuProps }">
                                    <v-btn size="small" :loading="exportLoading" v-bind="menuProps">
                                        <template #prepend>
                                            <FontAwesomeIcon :icon="faDownload" />
                                        </template>
                                        {{ t("StoreSummaryView.export") }}
                                        <template #append>
                                            <FontAwesomeIcon :icon="faChevronDown" size="sm" />
                                        </template>
                                    </v-btn>
                                </template>
                                <v-list density="compact">
                                    <v-list-item @click="exportData('csv')">
                                        <v-list-item-title>CSV (.csv)</v-list-item-title>
                                    </v-list-item>
                                    <v-list-item @click="exportData('xlsx')">
                                        <v-list-item-title>Excel (.xlsx)</v-list-item-title>
                                    </v-list-item>
                                    <v-list-item @click="exportData('ods')">
                                        <v-list-item-title>LibreOffice (.ods)</v-list-item-title>
                                    </v-list-item>
                                </v-list>
                            </v-menu>
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
    </LayoutBase>
</template>

<script setup lang="ts">
import {
    BarElement,
    CategoryScale,
    Chart as ChartJS,
    Legend,
    LinearScale,
    Title,
    Tooltip,
} from "chart.js";
import {
    faBoxOpen,
    faChevronDown,
    faDownload,
    faEuroSign,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { parseInt } from "lodash-es";
import { computed, onMounted, ref, type Ref } from "vue";
import { useI18n } from "vue-i18n";
import { Bar } from "vue-chartjs";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { StoreItem, StoreTransaction, TransactionItem } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/LayoutBase.vue";
import { useEvents } from "@/services/events";
import { downloadSpreadsheet, type SpreadsheetFormat } from "@/utils/spreadsheet";

// Register Chart.js components
ChartJS.register(BarElement, CategoryScale, Legend, LinearScale, Title, Tooltip);

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
const loading = ref(false);
const exportLoading = ref(false);

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

// Chart options
const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false,
        },
    },
    scales: {
        y: {
            beginAtZero: true,
            ticks: {
                stepSize: 1,
            },
        },
    },
};

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

// Build transaction ID to paid time map
const transactionPaidTimeMap = computed(() => {
    const map = new Map<number, Date>();
    for (const tx of paidTransactions.value) {
        if (tx.time_paid) {
            map.set(tx.id, new Date(tx.time_paid));
        }
    }
    return map;
});

// Sales per day chart data
const salesPerDayData = computed(() => {
    if (paidTransactions.value.length === 0) {
        return { labels: [], datasets: [] };
    }

    // Group sales by date
    const salesByDate = new Map<string, number>();
    for (const txItem of paidTransactionItems.value) {
        const paidTime = transactionPaidTimeMap.value.get(txItem.transaction);
        if (paidTime) {
            const dateKey = paidTime.toISOString().slice(0, 10);
            salesByDate.set(dateKey, (salesByDate.get(dateKey) ?? 0) + 1);
        }
    }

    // Get date range and fill in all days
    const sortedDates = Array.from(salesByDate.keys()).sort();
    if (sortedDates.length === 0) {
        return { labels: [], datasets: [] };
    }

    const labels: string[] = [];
    const data: number[] = [];
    const firstDate = sortedDates[0];
    const lastDate = sortedDates[sortedDates.length - 1];
    if (!firstDate || !lastDate) {
        return { labels: [], datasets: [] };
    }
    const startDate = new Date(firstDate);
    const endDate = new Date(lastDate);

    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
        const dateKey = d.toISOString().slice(0, 10);
        labels.push(dateKey);
        data.push(salesByDate.get(dateKey) ?? 0);
    }

    return {
        labels,
        datasets: [
            {
                label: t("StoreSummaryView.charts.salesCount"),
                data,
                backgroundColor: "#4CAF50",
            },
        ],
    };
});

// Sales by hour chart data
const salesByHourData = computed(() => {
    if (paidTransactionItems.value.length === 0) {
        return { labels: [], datasets: [] };
    }

    // Group sales by hour
    const salesByHour = new Array(24).fill(0);
    for (const txItem of paidTransactionItems.value) {
        const paidTime = transactionPaidTimeMap.value.get(txItem.transaction);
        if (paidTime) {
            const hour = paidTime.getHours();
            salesByHour[hour]++;
        }
    }

    // Only show hours with sales and nearby hours
    const labels: string[] = [];
    const data: number[] = [];
    for (let i = 0; i < 24; i++) {
        labels.push(`${i.toString().padStart(2, "0")}:00`);
        data.push(salesByHour[i]);
    }

    return {
        labels,
        datasets: [
            {
                label: t("StoreSummaryView.charts.salesCount"),
                data,
                backgroundColor: "#2196F3",
            },
        ],
    };
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
    loading.value = true;
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
    } finally {
        loading.value = false;
    }
}

function exportData(format: SpreadsheetFormat): void {
    exportLoading.value = true;
    try {
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
        toast.success(t("StoreSummaryView.exportSuccess"));
    } catch (e) {
        toast.error(t("StoreSummaryView.exportFailure"));
        console.error(e);
    } finally {
        exportLoading.value = false;
    }
}

onMounted(loadData);
</script>
