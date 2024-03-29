<template>
    <v-navigation-drawer color="grey-darken-4">
        <div class="fill-height d-flex flex-column ma-0 pa-0">
            <div class="d-flex flex-row ma-5 flex-0-0">
                <v-img :src="logoImage" />
                <h1 class="pl-2">{{ t("MainNavigation.title") }}</h1>
            </div>
            <v-divider />
            <v-select
                class="ma-2 flex-0-0"
                :label="t('MainNavigation.event')"
                variant="outlined"
                density="compact"
                :items="events"
                v-model="event"
            />
            <v-divider />
            <NavigationList :items="primary" :event="event" class="mb-auto" />
            <NavigationList :items="secondary" :event="event" class="mt-auto" />
        </div>
    </v-navigation-drawer>
</template>

<script setup lang="ts">
import logoImage from "@/assets/icon.png";
import { useRoute, useRouter } from "vue-router";
import { computed, onMounted, type Ref, ref, watch } from "vue";
import { useEvents } from "@/services/events";
import { useAuth } from "@/services/auth";
import { useI18n } from "vue-i18n";
import NavigationList, { type NavigationLinks } from "@/components/NavigationList.vue";

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
