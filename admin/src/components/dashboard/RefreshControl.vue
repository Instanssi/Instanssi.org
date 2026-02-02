<template>
    <div class="d-flex justify-end align-center text-grey-darken-1 text-caption">
        <span v-if="lastRefreshTime" class="mr-2">
            {{ t("RefreshControl.lastRefresh") }}: {{ d(lastRefreshTime, "long") }}
        </span>
        <v-select
            v-model="interval"
            :items="intervalOptions"
            density="compact"
            variant="outlined"
            hide-details
            style="max-width: 100px"
        />
    </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

const emit = defineEmits<{
    refresh: [];
}>();

const { t, d } = useI18n();

const intervalOptions = [
    { title: "10s", value: 10 * 1000 },
    { title: "30s", value: 30 * 1000 },
    { title: "1m", value: 60 * 1000 },
    { title: "5m", value: 5 * 60 * 1000 },
    { title: "15m", value: 15 * 60 * 1000 },
];

const interval = ref(5 * 60 * 1000); // Default 5 minutes
const lastRefreshTime = ref<Date | null>(null);
let refreshTimer: ReturnType<typeof setInterval> | null = null;

function triggerRefresh() {
    lastRefreshTime.value = new Date();
    emit("refresh");
}

function startTimer() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
    refreshTimer = setInterval(triggerRefresh, interval.value);
}

watch(interval, startTimer);

onMounted(() => {
    triggerRefresh();
    startTimer();
});

onUnmounted(() => {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
});
</script>
