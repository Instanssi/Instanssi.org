<template>
    <v-card>
        <v-card-title>
            <FontAwesomeIcon v-if="icon" :icon="icon" class="mr-2" />
            {{ title }}
        </v-card-title>
        <v-card-text>
            <div v-if="hasData" :style="{ height: `${height}px` }">
                <slot />
            </div>
            <div v-else class="text-center text-grey py-8">
                {{ noDataText }}
            </div>
        </v-card-text>
    </v-card>
</template>

<script setup lang="ts">
import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

withDefaults(
    defineProps<{
        title: string;
        hasData: boolean;
        noDataText: string;
        icon?: IconDefinition;
        height?: number;
    }>(),
    {
        icon: undefined,
        height: 300,
    }
);
</script>
