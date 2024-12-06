<template>
    <v-container>
        <v-col>
            <v-row>
                <h2 class="mb-4">
                    {{ title }}
                </h2>
            </v-row>
        </v-col>
        <slot />
    </v-container>
</template>

<script setup lang="ts">
defineProps<{ title: string }>();
</script>
