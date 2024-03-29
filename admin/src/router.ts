import { createRouter, createWebHistory } from "vue-router";
import { useAuth } from "@/services/auth";

const authService = useAuth();
const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/login",
            name: "login",
            meta: {
                requireAuth: false,
            },
            component: () => import("@/views/LoginView.vue"),
        },
        {
            path: "/logout",
            name: "logout",
            meta: {
                requireAuth: true,
            },
            component: {
                async beforeRouteEnter(to, from, next) {
                    await authService.logout();
                    next({ name: "login" });
                },
            },
        },
        {
            path: "/:eventId(\\d+)/events",
            name: "events",
            meta: {
                requireAuth: true,
            },
            props: true,
            component: () => import("@/views/EventView.vue"),
        },
        {
            path: "/:eventId(\\d+)/blog",
            name: "blog",
            meta: {
                requireAuth: true,
            },
            props: true,
            component: () => import("@/views/BlogEditorView.vue"),
        },
        {
            path: "/:eventId(\\d+)/",
            name: "dashboard",
            meta: {
                requireAuth: true,
            },
            component: () => import("@/views/MainView.vue"),
        },
        {
            path: "/",
            name: "index",
            meta: {
                requireAuth: true,
            },
            props: {
                eventId: undefined,
            },
            component: () => import("@/views/MainView.vue"),
        },
    ],
});

router.beforeEach((to, from, next) => {
    if (to.meta.requireAuth && !authService.isLoggedIn()) {
        next({ name: "login" });
    } else if (to.name === "login" && authService.isLoggedIn()) {
        next({ name: "dashboard" });
    } else {
        next();
    }
});

export default router;
