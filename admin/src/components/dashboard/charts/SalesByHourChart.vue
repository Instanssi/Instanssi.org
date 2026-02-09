<template>
    <ChartCard
        :title="t('StoreSummaryView.charts.salesByHour')"
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
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { Bar } from "vue-chartjs";

import ChartCard from "@/components/dashboard/ChartCard.vue";

ChartJS.register(BarElement, CategoryScale, Legend, LinearScale, Tooltip);

const props = defineProps<{
    salesPerHour: Array<{ hour: number; count: number }>;
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
    if (props.salesPerHour.length === 0) {
        return { labels: [], datasets: [] };
    }

    // Build hour -> count map from pre-aggregated data
    const salesByHour = new Array(24).fill(0);
    for (const row of props.salesPerHour) {
        salesByHour[row.hour] = row.count;
    }

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
</script>
