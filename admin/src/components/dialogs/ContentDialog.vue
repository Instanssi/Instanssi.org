<template>
    <v-dialog v-model="visible" :max-width="maxWidth" :scrollable="scrollable">
        <v-card>
            <v-card-title class="d-flex justify-space-between align-center">
                <div class="d-flex align-center">
                    <span>{{ title }}</span>
                    <slot name="title-actions" />
                </div>
                <v-btn icon variant="text" density="compact" @click="visible = false">
                    <FontAwesomeIcon :icon="faXmark" />
                </v-btn>
            </v-card-title>
            <v-divider />
            <v-card-text :class="contentClass">
                <slot />
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script setup lang="ts">
import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

withDefaults(
    defineProps<{
        title: string;
        maxWidth?: number;
        scrollable?: boolean;
        contentClass?: string;
    }>(),
    {
        maxWidth: 600,
        scrollable: false,
        contentClass: undefined,
    }
);

const visible = defineModel<boolean>({ default: false });
</script>
