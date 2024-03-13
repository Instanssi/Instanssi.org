<template>
    <v-app>
        <Navigation
            v-if="authService.isLoggedIn()"
            :items="navLinks"
        />
        <v-main :class="backgroundClass">
            <RouterView />
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import Navigation, { type NavigationLinks } from "@/components/MainNavigation.vue";
import { useAuth } from "@/services/auth";
import { computed } from "vue";

const backgroundClass = computed(() =>
    authService.isLoggedIn() ? undefined : "login-view"
);
const authService = useAuth();
const navLinks: NavigationLinks = [
    {
        title: "Dashboard",
        icon: "fas fa-dashboard",
        to: "dashboard",
    },
    {
        title: "Site",
        icon: "fas fa-sitemap",
        children: [
            {
                title: "Blog",
                icon: "fas fa-blog",
                to: "blog",
            },
        ],
    },
    {
        title: "Log out",
        icon: "fas fa-right-from-bracket",
        to: "logout",
    },
];
</script>

<style scoped lang="scss">
.login-view {
    background-image: url("@/assets/webtausta.jpg");
    background-repeat: no-repeat;
    background-size: cover;
}
</style>
