<template>
    <span>{{ formattedDate }}</span>
</template>

<script setup lang="ts">
/**
 * DateCell - Display date-only values (from Django DateField)
 * For datetime values with time, use DateTimeCell instead.
 */
import { Temporal } from "temporal-polyfill";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

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

const formattedDate = computed(() => {
    if (!props.value) return props.fallback;

    const plainDate = Temporal.PlainDate.from(props.value);
    const options: Intl.DateTimeFormatOptions =
        props.format === "short" ? { dateStyle: "short" } : { dateStyle: "long" };
    return new Intl.DateTimeFormat(locale.value, options).format(
        new Date(plainDate.year, plainDate.month - 1, plainDate.day)
    );
});
</script>
