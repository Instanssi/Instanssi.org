<template>
    <v-list density="compact" open-strategy="multiple" nav>
        <template v-for="item in filterLinks(items)">
            <v-list-group v-if="item.children" :key="`group-${item.title}`">
                <template v-slot:activator="{ props }">
                    <v-list-item v-bind="props" :prepend-icon="item.icon" :title="item.title" />
                </template>
                <v-list-item
                    v-for="child in filterLinks(item.children)"
                    :key="`${item.title}-${child.title}`"
                    :prepend-icon="child.icon"
                    :title="child.title"
                    @click="navigateTo(child.to)"
                />
            </v-list-group>
            <v-list-item
                v-else
                :key="`root-${item.title}`"
                :prepend-icon="item.icon"
                :title="item.title"
                @click="navigateTo(item.to)"
            />
        </template>
    </v-list>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { toRefs } from "vue";
import { PermissionTarget, useAuth } from "@/services/auth";

export type NavigationLink = {
    title: string;
    icon: string;
    to?: string;
    children?: NavigationLink[];
    requirePerm?: PermissionTarget;
};
export type NavigationLinks = NavigationLink[];

const props = defineProps<{ items: NavigationLinks; event: number | undefined }>();

const router = useRouter();
const authService = useAuth();
const { event } = toRefs(props);

function filterLinks(items: NavigationLinks): NavigationLinks {
    return items.filter((m) => !m.requirePerm || authService.canView(m.requirePerm));
}

function navigateTo(to: string | undefined): void {
    if (!to) return;
    router.push({ name: to, params: { eventId: event.value } });
}
</script>
