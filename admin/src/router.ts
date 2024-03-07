import { createRouter, createWebHistory } from "vue-router";

const DashboardView = () => import("@/views/DashBoard.vue");

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "home",
            component: DashboardView,
        },
    ],
});

export default router;
