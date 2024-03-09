<template>
    <v-app>
        <Navigation v-if="authService.isLoggedIn()" :items="navLinks" />
        <v-main class="bg-grey-darken-3">
            <RouterView />
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import Navigation, { type NavigationLinks } from "@/components/MainNavigation.vue";
import { useAuth } from "@/services/auth";

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

<style scoped lang="scss"></style>
