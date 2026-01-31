<template>
    <v-chip :color="chipColor" size="small">
        {{ displayText }}
    </v-chip>
</template>

<script setup lang="ts">
import { Temporal } from "temporal-polyfill";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import { ADMIN_TIMEZONE } from "@/utils/datetime";

const props = defineProps<{
    /** Event date in YYYY-MM-DD format */
    date: string;
}>();

const { t } = useI18n();

const daysUntil = computed(() => {
    const eventDate = Temporal.PlainDate.from(props.date);
    const today = Temporal.Now.zonedDateTimeISO(ADMIN_TIMEZONE).toPlainDate();
    return eventDate.since(today).days;
});

const displayText = computed(() => {
    const days = daysUntil.value;
    if (days > 0) {
        return t("MainView.daysUntil", { days });
    } else if (days === 0) {
        return t("MainView.today");
    } else {
        return t("MainView.daysAgo", { days: Math.abs(days) });
    }
});

const chipColor = computed(() => {
    const days = daysUntil.value;
    if (days > 7) return "green";
    if (days > 0) return "orange";
    if (days === 0) return "red";
    return "grey";
});
</script>
