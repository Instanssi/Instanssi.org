<template>
    <!-- Mobile App Bar -->
    <v-app-bar v-if="mobile" color="grey-darken-4" density="compact">
        <v-app-bar-nav-icon @click="drawer = !drawer" />
        <v-app-bar-title>{{ t("MainNavigation.title") }}</v-app-bar-title>
    </v-app-bar>

    <!-- Navigation Drawer (permanent on desktop, temporary on mobile) -->
    <v-navigation-drawer
        v-model="drawer"
        color="grey-darken-4"
        :permanent="!mobile"
        :temporary="mobile"
    >
        <div class="fill-height d-flex flex-column ma-0 pa-0">
            <div class="d-flex flex-row ma-5 flex-0-0">
                <v-img :src="logoImage" max-width="32" />
                <h1 class="pl-2">
                    {{ t("MainNavigation.title") }}
                </h1>
            </div>
            <v-divider />
            <v-select
                :model-value="event"
                class="ma-2 flex-0-0 nav-event-select"
                :label="t('MainNavigation.event')"
                variant="outlined"
                density="compact"
                :items="events"
                @update:model-value="onEventChange"
            >
                <template v-if="authService.canView(PermissionTarget.EVENT)" #append>
                    <v-btn
                        variant="plain"
                        density="compact"
                        class="event-btn"
                        @click="routeToEvents"
                    >
                        <FontAwesomeIcon :icon="faCalendarDays" class="ma-0 pa-0" />
                    </v-btn>
                </template>
            </v-select>
            <v-divider />
            <NavigationList
                :items="primary"
                :event="event"
                class="mb-auto"
                @navigate="onNavigate"
            />
            <NavigationList
                :items="secondary"
                :event="event"
                class="mt-auto"
                @navigate="onNavigate"
            />
        </div>
    </v-navigation-drawer>
</template>

<script setup lang="ts">
import { faCalendarDays } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { type Ref, computed, inject, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { useDisplay } from "vuetify";

import logoImage from "@/assets/icon.png";
import NavigationList, { type NavigationLinks } from "@/components/layout/NavigationList.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { confirmDialogKey, type ConfirmDialogType } from "@/symbols";

defineProps<{ primary: NavigationLinks; secondary: NavigationLinks }>();

const router = useRouter();
const route = useRoute();
const eventService = useEvents();
const authService = useAuth();
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;
const { t } = useI18n();
const { mobile } = useDisplay();

const drawer = ref(true);
const event: Ref<undefined | number> = ref(undefined);
const events = computed(() =>
    eventService.getEvents().map((item) => ({ title: item.name, value: item.id }))
);

/**
 * Close drawer on mobile after navigation
 */
function onNavigate() {
    if (mobile.value) {
        drawer.value = false;
    }
}

/**
 * Check if the current route is an edit or create page.
 */
function isOnEditOrCreatePage(): boolean {
    const routeName = route.name?.toString() ?? "";
    return routeName.endsWith("-edit") || routeName.endsWith("-new");
}

/**
 * Handle event selection from dropdown. Ask for confirmation if on edit/create page
 * and redirect to dashboard. Otherwise, stay on the same page with the new event.
 */
async function onEventChange(newEvent: number | undefined): Promise<void> {
    if (newEvent === event.value) return;

    if (isOnEditOrCreatePage()) {
        const confirmed = await confirmDialog.value?.confirm(
            t("MainNavigation.confirmEventChange")
        );
        if (!confirmed) return;
        event.value = newEvent;
        router.push({ name: "dashboard", params: { eventId: newEvent } });
    } else {
        event.value = newEvent;
        router.push({
            name: route.name!,
            params: { ...route.params, eventId: newEvent },
            query: route.query,
        });
    }
    onNavigate();
}

function routeToEvents(): void {
    router.push({ name: "events" });
    onNavigate();
}

/**
 * Initialize event selection from the latest event.
 */
async function initEvents() {
    await eventService.refreshEvents();
    const latest = eventService.getLatestEvent();
    if (latest) {
        event.value = latest.id;
    }
}

/**
 * React to events list changes.
 */
function onEventsChange() {
    const allEvents = eventService.getEvents();
    if (allEvents.length === 0) {
        event.value = undefined;
    } else if (!event.value) {
        const latest = eventService.getLatestEvent();
        if (latest) {
            event.value = latest.id;
        }
    }
}

watch(() => authService.isLoggedIn(), initEvents);
watch(() => eventService.getEvents(), onEventsChange);
onMounted(initEvents);
</script>

<style lang="scss">
.nav-event-select .v-input__append {
    margin-inline-start: 8px !important;
}
.event-btn {
    min-width: 0;
    margin: 0.2rem;
}
</style>
