<template>
    <v-list density="compact" open-strategy="multiple" nav>
        <template v-for="item in filterLinks(items)">
            <v-list-group v-if="item.children" :key="`group-${item.title}`">
                <template #activator="{ props }">
                    <v-list-item v-bind="props" :prepend-icon="item.icon" :title="item.title" />
                </template>
                <v-list-item
                    v-for="child in filterLinks(item.children)"
                    :key="`${item.title}-${child.title}`"
                    :prepend-icon="child.icon"
                    :title="child.title"
                    :to="navigateTo(child)"
                />
            </v-list-group>
            <v-list-item
                v-else
                :key="`root-${item.title}`"
                :prepend-icon="item.icon"
                :title="item.title"
                :to="navigateTo(item)"
            />
        </template>
    </v-list>
</template>

<script setup lang="ts">
import { toRefs } from "vue";
import { type RouteLocationRaw } from "vue-router";

import { PermissionTarget, useAuth } from "@/services/auth";

export type NavigationLink = {
    title: string;
    icon: string;
    to?: string;
    children?: NavigationLink[];
    requirePerm?: PermissionTarget;
    noEventId?: boolean;
};
export type NavigationLinks = NavigationLink[];

const props = defineProps<{ items: NavigationLinks; event: number | undefined }>();

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
