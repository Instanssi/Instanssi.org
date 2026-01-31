<template>
    <v-menu>
        <template #activator="{ props: menuProps }">
            <v-btn :size="size" :loading="loading" v-bind="menuProps">
                <template #prepend>
                    <FontAwesomeIcon :icon="faDownload" />
                </template>
                {{ label }}
                <template #append>
                    <FontAwesomeIcon :icon="faChevronDown" size="sm" />
                </template>
            </v-btn>
        </template>
        <v-list density="compact">
            <v-list-item @click="emit('export', 'csv')">
                <v-list-item-title>CSV (.csv)</v-list-item-title>
            </v-list-item>
            <v-list-item @click="emit('export', 'xlsx')">
                <v-list-item-title>Excel (.xlsx)</v-list-item-title>
            </v-list-item>
            <v-list-item @click="emit('export', 'ods')">
                <v-list-item-title>LibreOffice (.ods)</v-list-item-title>
            </v-list-item>
        </v-list>
    </v-menu>
</template>

<script setup lang="ts">
import { faChevronDown, faDownload } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

import type { SpreadsheetFormat } from "@/utils/spreadsheet";

withDefaults(
    defineProps<{
        label: string;
        loading?: boolean;
        size?: "x-small" | "small" | "default" | "large" | "x-large";
    }>(),
    {
        loading: false,
        size: "default",
    }
);

const emit = defineEmits<{
    export: [format: SpreadsheetFormat];
}>();
</script>
