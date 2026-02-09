<template>
    <LayoutBase :key="`store-summary-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <!-- Summary Cards -->
            <v-row>
                <v-col cols="12" sm="6">
                    <StatCard
                        :icon="faBoxOpen"
                        :value="summary?.total_items_sold ?? 0"
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
                    <SalesPerDayChart :sales-per-day="summary?.sales_per_day ?? []" />
                </v-col>
                <v-col cols="12" md="6">
                    <SalesByHourChart :sales-per-hour="summary?.sales_per_hour ?? []" />
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
                                    {{ parseFloat(item.revenue).toFixed(2) }} &euro;
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

import * as api from "@/api";
import type { StoreSummary } from "@/api";
import RefreshControl from "@/components/dashboard/RefreshControl.vue";
import SalesByHourChart from "@/components/dashboard/charts/SalesByHourChart.vue";
import SalesPerDayChart from "@/components/dashboard/charts/SalesPerDayChart.vue";
import ExportButton from "@/components/form/ExportButton.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import StatCard from "@/components/dashboard/StatCard.vue";
import { useEvents } from "@/services/events";
import { useAsyncAction } from "@/composables/useAsyncAction";
import { downloadSpreadsheet, type SpreadsheetFormat } from "@/utils/spreadsheet";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

interface SummaryRow {
    item: string;
    variant: string;
    quantity: number;
    revenue: string;
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

const summary: Ref<StoreSummary | null> = ref(null);

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

const summaryRows = computed<SummaryRow[]>(() => {
    if (!summary.value) return [];
    return summary.value.items.map((row) => ({
        item: row.item_name,
        variant: row.variant_name ?? "-",
        quantity: row.quantity,
        revenue: row.revenue,
    }));
});

const totalRevenue = computed(() => {
    if (!summary.value) return 0;
    return parseFloat(summary.value.total_revenue);
});

async function loadData() {
    try {
        const response = await api.adminEventStoreSummaryList({
            path: { event_pk: eventId.value },
        });
        // The API returns a single object (not an array despite the generated type)
        summary.value = response.data as unknown as StoreSummary;
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
            data.push([row.item, row.variant, row.quantity, parseFloat(row.revenue).toFixed(2)]);
        }

        // Add totals row
        data.push([]);
        data.push([
            "TOTAL",
            "",
            summary.value?.total_items_sold ?? 0,
            totalRevenue.value.toFixed(2),
        ]);

        downloadSpreadsheet(data, "instanssi_sales_summary", format, "Sales Summary");
    });
}
</script>
