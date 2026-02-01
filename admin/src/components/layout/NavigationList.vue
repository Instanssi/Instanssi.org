<template>
    <v-list density="compact" open-strategy="multiple" nav>
        <template v-for="item in filterLinks(items)">
            <v-list-group v-if="item.children" :key="`group-${item.title}`">
                <template #activator="{ props }">
                    <v-list-item v-bind="props" :title="item.title">
                        <template #prepend>
                            <FontAwesomeIcon :icon="item.icon" class="nav-icon" />
                        </template>
                    </v-list-item>
                </template>
                <v-list-item
                    v-for="child in filterLinks(item.children)"
                    :key="`${item.title}-${child.title}`"
                    :title="child.title"
                    :to="navigateTo(child)"
                    @click="emit('navigate')"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="child.icon" class="nav-icon" />
                    </template>
                </v-list-item>
            </v-list-group>
            <v-list-item
                v-else
                :key="`root-${item.title}`"
                :title="item.title"
                :to="navigateTo(item)"
                @click="emit('navigate')"
            >
                <template #prepend>
                    <FontAwesomeIcon :icon="item.icon" class="nav-icon" />
                </template>
            </v-list-item>
        </template>
    </v-list>
</template>

<script setup lang="ts">
import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { toRefs } from "vue";
import { type RouteLocationRaw } from "vue-router";

import { PermissionTarget, useAuth } from "@/services/auth";

export type NavigationLink = {
    title: string;
    icon: IconDefinition;
    to?: string;
    children?: NavigationLink[];
    requirePerm?: PermissionTarget;
    noEventId?: boolean;
};
export type NavigationLinks = NavigationLink[];

const props = defineProps<{ items: NavigationLinks; event: number | undefined }>();
const emit = defineEmits<{ navigate: [] }>();

const authService = useAuth();
const { event } = toRefs(props);

function filterLinks(items: NavigationLinks): NavigationLinks {
    return items
        .filter((m) => !m.requirePerm || authService.canView(m.requirePerm))
        .filter((m) => !!m.noEventId || !!event.value);
}

function navigateTo(item: NavigationLink): RouteLocationRaw | undefined {
    if (!item.to) return;
    return {
        name: item.to,
        params: item.noEventId ? {} : { eventId: event.value!.toString() },
    };
}
</script>

<style scoped>
.v-list-group :deep(.v-list-group__items .v-list-item) {
    padding-inline-start: 32px !important;
}

.nav-icon {
    width: 24px;
    margin-right: 12px;
    opacity: 0.7;
}
</style>
