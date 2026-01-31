<template>
    <ChartCard
        :title="t('MainView.charts.entriesPerCompo')"
        :icon="faChartPie"
        :has-data="chartData.labels.length > 0"
        :no-data-text="t('MainView.charts.noData')"
    >
        <Pie :data="chartData" :options="chartOptions" />
    </ChartCard>
</template>

<script setup lang="ts">
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from "chart.js";
import { faChartPie } from "@fortawesome/free-solid-svg-icons";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { Pie } from "vue-chartjs";

import ChartCard from "@/components/dashboard/ChartCard.vue";

ChartJS.register(ArcElement, Legend, Tooltip);

const props = defineProps<{
    compos: Array<{ id: number; name: string }>;
    entryCounts: Map<number, number>;
}>();

const { t } = useI18n();

const chartColors = [
    "#4CAF50",
    "#2196F3",
    "#FF9800",
    "#9C27B0",
    "#E91E63",
    "#00BCD4",
    "#FFEB3B",
    "#795548",
    "#607D8B",
    "#F44336",
];

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: "right" as const,
        },
    },
};

const chartData = computed(() => ({
    labels: props.compos.map((c) => c.name),
    datasets: [
        {
            data: props.compos.map((c) => props.entryCounts.get(c.id) ?? 0),
            backgroundColor: chartColors.slice(0, props.compos.length),
        },
    ],
}));
</script>
