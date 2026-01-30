<template>
    <v-container>
        <v-col>
            <v-breadcrumbs :items="breadcrumbs">
                <template #divider>
                    <FontAwesomeIcon
                        :icon="faChevronRight"
                        size="xs"
                        class="text-medium-emphasis"
                    />
                </template>
                <template #item="{ item, index }">
                    <span v-if="index === breadcrumbs.length - 1" class="text-h6 font-weight-bold">
                        {{ item.title }}
                    </span>
                    <router-link
                        v-else-if="item.to"
                        :to="item.to"
                        class="text-medium-emphasis text-decoration-none"
                    >
                        {{ item.title }}
                    </router-link>
                    <span v-else class="text-medium-emphasis">
                        {{ item.title }}
                    </span>
                </template>
            </v-breadcrumbs>
        </v-col>
        <slot />
    </v-container>
</template>

<script setup lang="ts">
import { faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

export type BreadcrumbItem = {
    title: string;
    to?: { name: string; params?: Record<string, string | number> };
    disabled?: boolean;
};

defineProps<{
    breadcrumbs: BreadcrumbItem[];
}>();
</script>
