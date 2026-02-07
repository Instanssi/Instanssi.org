<template>
    <v-tooltip v-if="disqualified && disqualifiedReason" location="top">
        <template #activator="{ props: tooltipProps }">
            <span v-bind="tooltipProps" style="cursor: help">
                <BooleanIcon :value="true" true-class="text-red" />
            </span>
        </template>
        {{ disqualifiedReason }}
    </v-tooltip>
    <BooleanIcon v-else :value="disqualified" true-class="text-red" false-class="text-green" />
</template>

<script setup lang="ts">
import BooleanIcon from "@/components/table/BooleanIcon.vue";

withDefaults(
    defineProps<{
        disqualified?: boolean;
        disqualifiedReason?: string | null;
    }>(),
    {
        disqualified: false,
    }
);
</script>
