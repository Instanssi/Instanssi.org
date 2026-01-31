<template>
    <ChartCard
        :title="t('MainView.charts.competitionParticipants')"
        :icon="faChartBar"
        :has-data="chartData.labels.length > 0"
        :no-data-text="t('MainView.charts.noData')"
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
import { faChartBar } from "@fortawesome/free-solid-svg-icons";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { Bar } from "vue-chartjs";

import ChartCard from "@/components/ChartCard.vue";

ChartJS.register(BarElement, CategoryScale, Legend, LinearScale, Tooltip);

const props = defineProps<{
    competitions: Array<{ id: number; name: string }>;
    participantCounts: Map<number, number>;
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

const chartData = computed(() => ({
    labels: props.competitions.map((c) => c.name),
    datasets: [
        {
            label: t("MainView.stats.participants"),
            data: props.competitions.map((c) => props.participantCounts.get(c.id) ?? 0),
            backgroundColor: "#2196F3",
        },
    ],
}));
</script>
