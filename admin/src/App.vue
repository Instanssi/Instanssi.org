<template>
    <v-app>
        <Navigation
            v-if="authService.isLoggedIn()"
            :primary="primaryLinks"
            :secondary="secondaryLinks"
        />
        <v-main :class="backgroundClass">
            <RouterView />
            <ConfirmDialog ref="confirmDialog" />
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import { computed, provide, ref } from "vue";
import { useI18n } from "vue-i18n";

import ConfirmDialog from "@/components/ConfirmDialog.vue";
import Navigation from "@/components/MainNavigation.vue";
import type { NavigationLinks } from "@/components/NavigationList.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { confirmDialogKey } from "@/symbols";

const { t } = useI18n();
const backgroundClass = computed(() => (authService.isLoggedIn() ? undefined : "login-view"));
const authService = useAuth();
const confirmDialog = ref(undefined);
const primaryLinks: NavigationLinks = [
    {
        title: t("App.nav.dashboard"),
        icon: "fas fa-dashboard",
        to: "dashboard",
    },
    {
        title: t("App.nav.blog"),
        icon: "fas fa-blog",
        to: "blog",
        requirePerm: PermissionTarget.BLOG_ENTRY,
    },
];
const secondaryLinks: NavigationLinks = [
    {
        title: t("App.nav.users"),
        icon: "fas fa-users",
        to: "users",
        noEventId: true,
    },
    {
        title: t("App.nav.logout"),
        icon: "fas fa-right-from-bracket",
        to: "logout",
        noEventId: true,
    },
];

provide(confirmDialogKey, confirmDialog);
</script>

<style scoped lang="scss">
.login-view {
    background-image: url("@/assets/webtausta.jpg");
    background-repeat: no-repeat;
    background-size: cover;
}
</style>

<style>
@import "vue-toastification/dist/index.css";
</style>
