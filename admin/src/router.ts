import { createRouter, createWebHistory } from "vue-router";

const DashboardView = () => import("@/views/DashBoard.vue");

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "dashboard",
            component: DashboardView,
        },
        {
            path: "/site/blog",
            name: "blog",
            component: DashboardView,
        },
        {
            path: "/logout",
            name: "logout",
            component: DashboardView,
        },
    ],
});

export default router;
