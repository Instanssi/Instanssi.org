<template>
    <span>{{ formattedPrice }}</span>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
    defineProps<{
        value?: string | number | null;
        currency?: string;
        fallback?: string;
    }>(),
    {
        value: null,
        currency: "€",
        fallback: "-",
    }
);

const formattedPrice = computed(() => {
    if (props.value === null || props.value === undefined) return props.fallback;
    return `${props.value} ${props.currency}`;
});
</script>
