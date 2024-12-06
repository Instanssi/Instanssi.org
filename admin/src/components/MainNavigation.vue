<template>
    <v-navigation-drawer color="grey-darken-4">
        <div class="fill-height d-flex flex-column ma-0 pa-0">
            <div class="d-flex flex-row ma-5 flex-0-0">
                <v-img :src="logoImage" />
                <h1 class="pl-2">
                    {{ t("MainNavigation.title") }}
                </h1>
            </div>
            <v-divider />
            <v-select
                v-model="event"
                class="ma-2 flex-0-0 nav-event-select"
                :label="t('MainNavigation.event')"
                variant="outlined"
                density="compact"
                :items="events"
            >
                <template v-if="authService.canView(PermissionTarget.EVENT)" #append>
                    <v-btn
                        icon="fas fa-calendar-days"
                        variant="plain"
                        density="compact"
                        @click="routeToEvents"
                    />
                </template>
            </v-select>
            <v-divider />
            <NavigationList :items="primary" :event="event" class="mb-auto" />
            <NavigationList :items="secondary" :event="event" class="mt-auto" />
        </div>
    </v-navigation-drawer>
</template>

<script setup lang="ts">
import { type Ref, computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import logoImage from "@/assets/icon.png";
import NavigationList, { type NavigationLinks } from "@/components/NavigationList.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";

defineProps<{ primary: NavigationLinks; secondary: NavigationLinks }>();

const router = useRouter();
const route = useRoute();
const eventService = useEvents();
const authService = useAuth();
const { t } = useI18n();
const event: Ref<undefined | number> = ref(undefined);
const events = computed(() =>
    eventService.getEvents().map((item) => ({ title: item.name, value: item.id }))
);

/**
 * When new event is selected from the select-box, try to immediately redirect the current view
 * to that event. Note that this may cause warning, if we are on a page that has no eventId parameter.
 * This is fine for now and should not break anything.
 */
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

function routeToEvents(): void {
    router.push({ name: "events" });
}

/**
 * If there are any events, get and set the latest one.
 */
function trySetLatestEvent() {
    const latest = eventService.getLatestEvent();
    if (latest) {
        event.value = latest.id;
    }
}

/**
 * If we get logged in, try to refresh events immediately.
 */
async function tryRefreshEvents() {
    await eventService.refreshEvents();
    trySetLatestEvent();
}

/**
 * React to events list changes. If we have no event, just set select-box to nothing.
 * If any events appear, select the first one.
 */
async function trySelectEvent() {
    const events = eventService.getEvents();
    if (events.length == 0) {
        event.value = undefined;
    } else {
        trySetLatestEvent();
    }
}

watch(event, changeEvent);
watch(authService.isLoggedIn, tryRefreshEvents);
watch(eventService.getEvents, trySelectEvent);
onMounted(tryRefreshEvents);
</script>

<style lang="scss">
.nav-event-select .v-input__append {
    margin-inline-start: 8px !important;
}
</style>
