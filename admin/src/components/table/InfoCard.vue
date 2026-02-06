<template>
    <v-card>
        <v-card-title>{{ title }}</v-card-title>
        <v-card-text>
            <v-table density="compact">
                <tbody>
                    <slot />
                </tbody>
            </v-table>
        </v-card-text>
    </v-card>
</template>

<script setup lang="ts">
defineProps<{
    title: string;
}>();
</script>
