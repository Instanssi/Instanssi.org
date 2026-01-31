<template>
    <v-card
        :color="color"
        variant="tonal"
        :class="{ 'cursor-pointer': clickable }"
        @click="clickable ? emit('click') : undefined"
    >
        <v-card-text class="d-flex align-center">
            <FontAwesomeIcon :icon="icon" size="2x" class="mr-4" />
            <div>
                <div class="text-h4">{{ value }}</div>
                <div class="text-body-2">{{ label }}</div>
                <div v-if="subtitle" class="text-caption text-grey">
                    {{ subtitle }}
                </div>
            </div>
        </v-card-text>
    </v-card>
</template>

<script setup lang="ts">
import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

defineProps<{
    icon: IconDefinition;
    value: string | number;
    label: string;
    color: string;
    subtitle?: string;
    clickable?: boolean;
}>();

const emit = defineEmits<{
    click: [];
}>();
</script>
