<template>
    <v-app>
        <Navigation :items="navLinks" />
        <v-main>
            <RouterView />
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import Navigation, { type NavigationLinks } from "@/components/MainNavigation.vue";

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

<style scoped></style>
