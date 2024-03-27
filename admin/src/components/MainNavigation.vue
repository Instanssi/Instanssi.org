<template>
    <v-navigation-drawer color="grey-darken-4">
        <div class="d-flex ma-5 align-center">
            <v-img :src="logoImage" />
            <h1 class="pl-2">{{ t("MainNavigation.title") }}</h1>
        </div>
        <v-divider />
        <v-select
            class="ma-1"
            :label="t('MainNavigation.event')"
            variant="outlined"
            density="compact"
            :items="events"
            v-model="event"
        />
        <v-divider />
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
    </v-navigation-drawer>
</template>

<script setup lang="ts">
import logoImage from "@/assets/icon.png";
import { useRoute, useRouter } from "vue-router";
import { computed, onMounted, type Ref, ref, watch } from "vue";
import { useEvents } from "@/services/events";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useI18n } from "vue-i18n";

export type NavigationLink = {
    title: string;
    icon: string;
    to?: string;
    children?: NavigationLink[];
    requirePerm?: PermissionTarget;
};
export type NavigationLinks = NavigationLink[];

defineProps<{ items: NavigationLinks }>();

const router = useRouter();
const route = useRoute();
const eventService = useEvents();
const authService = useAuth();
const { t } = useI18n();
const event: Ref<undefined | number> = ref(undefined);
const events = computed(() =>
    eventService.getEvents().map((item) => ({ title: item.name, value: item.id }))
);

function filterLinks(items: NavigationLinks): NavigationLinks {
    return items.filter((m) => !m.requirePerm || authService.canView(m.requirePerm));
}

function changeEvent(): void {
    router.push({
        name: route.name!,
        params: {
            ...route.params,
            eventId: event.value,
        },
        query: route.query,
    });
}

function navigateTo(to: string | undefined): void {
    if (!to) return;
    router.push({ name: to, params: { eventId: event.value } });
}

async function tryRefreshEvents() {
    await eventService.refreshEvents();
    const latest = eventService.getLatestEvent();
    if (!latest) {
        await router.push({ name: "dashboard" });
    } else {
        event.value = latest.id;
    }
}

watch(event, changeEvent);
watch(authService.isLoggedIn, tryRefreshEvents);
onMounted(tryRefreshEvents);
</script>

<style scoped lang="scss">
h1 {
    font-size: 1.9em;
    text-transform: uppercase;
}
</style>
