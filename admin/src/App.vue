<template>
    <v-app>
        <Navigation v-if="authService.isLoggedIn()" :items="navLinks" />
        <v-main :class="backgroundClass">
            <RouterView />
            <ConfirmDialog ref="confirmDialog" />
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import Navigation, { type NavigationLinks } from "@/components/MainNavigation.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { computed, provide, ref } from "vue";
import { useI18n } from "vue-i18n";
import ConfirmDialog from "@/components/ConfirmDialog.vue";
import { confirmDialogKey } from "@/symbols";

const { t } = useI18n();
const backgroundClass = computed(() => (authService.isLoggedIn() ? undefined : "login-view"));
const authService = useAuth();
const confirmDialog = ref(undefined);
const navLinks: NavigationLinks = [
    {
        title: t("App.nav.dashboard"),
        icon: "fas fa-dashboard",
        to: "dashboard",
    },
    {
        title: t("App.nav.site"),
        icon: "fas fa-sitemap",
        children: [
            {
                title: t("App.nav.blog"),
                icon: "fas fa-blog",
                to: "blog",
                requirePerm: PermissionTarget.BLOG_ENTRY,
            },
        ],
    },
    {
        title: t("App.nav.logout"),
        icon: "fas fa-right-from-bracket",
        to: "logout",
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
