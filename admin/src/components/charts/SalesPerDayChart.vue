<template>
    <ChartCard
        :title="t('StoreSummaryView.charts.salesPerDay')"
        :has-data="chartData.labels.length > 0"
        :no-data-text="t('StoreSummaryView.charts.noData')"
    >
        <Bar :data="chartData" :options="chartOptions" />
    </ChartCard>
</template>

<script setup lang="ts">
import {
    BarElement,
    CategoryScale,
    Chart as ChartJS,
    Legend,
    LinearScale,
    Tooltip,
} from "chart.js";
import { Temporal } from "temporal-polyfill";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { Bar } from "vue-chartjs";

import ChartCard from "@/components/ChartCard.vue";

ChartJS.register(BarElement, CategoryScale, Legend, LinearScale, Tooltip);

const props = defineProps<{
    paidTimes: Temporal.ZonedDateTime[];
}>();

const { t } = useI18n();

const chartOptions = {
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

const chartData = computed(() => {
    if (props.paidTimes.length === 0) {
        return { labels: [], datasets: [] };
    }

    // Group sales by date (in Helsinki timezone)
    const salesByDate = new Map<string, number>();
    for (const paidTime of props.paidTimes) {
        const dateKey = paidTime.toPlainDate().toString();
        salesByDate.set(dateKey, (salesByDate.get(dateKey) ?? 0) + 1);
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

    // Iterate through date range using Temporal
    let currentDate = Temporal.PlainDate.from(firstDate);
    const endDate = Temporal.PlainDate.from(lastDate);
    while (Temporal.PlainDate.compare(currentDate, endDate) <= 0) {
        const dateKey = currentDate.toString();
        labels.push(dateKey);
        data.push(salesByDate.get(dateKey) ?? 0);
        currentDate = currentDate.add({ days: 1 });
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
</script>
