<template>
    <span>{{ formattedDateTime }}</span>
</template>

<script setup lang="ts">
/**
 * DateTimeCell - Display datetime values with time (from Django DateTimeField)
 * For date-only values, use DateCell instead.
 */
import { Temporal } from "temporal-polyfill";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import { ADMIN_TIMEZONE } from "@/utils/datetime";

const props = withDefaults(
    defineProps<{
        value?: string | null;
        format?: "short" | "long";
        fallback?: string;
    }>(),
    {
        value: null,
        format: "long",
        fallback: "-",
    }
);

const { locale } = useI18n();

const formattedDateTime = computed(() => {
    if (!props.value) return props.fallback;

    const instant = Temporal.Instant.from(props.value);
    const zoned = instant.toZonedDateTimeISO(ADMIN_TIMEZONE);

    const options: Intl.DateTimeFormatOptions =
        props.format === "short"
            ? { dateStyle: "short", timeStyle: "short", timeZone: ADMIN_TIMEZONE, hour12: false }
            : { dateStyle: "long", timeStyle: "short", timeZone: ADMIN_TIMEZONE, hour12: false };

    return new Intl.DateTimeFormat(locale.value, options).format(new Date(zoned.epochMilliseconds));
});
</script>
