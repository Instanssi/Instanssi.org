import { createRouter, createWebHistory } from "vue-router";
import { useAuth } from "@/services/auth";

const authService = useAuth();
const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/management/login",
            name: "login",
            meta: {
                requireAuth: false,
            },
            component: () => import("@/views/LoginView.vue"),
        },
        {
            path: "/management/site/blog",
            name: "blog",
            meta: {
                requireAuth: true,
            },
            component: () => import("@/views/BlogEditorView.vue"),
        },
        {
            path: "/management/logout",
            name: "logout",
            meta: {
                requireAuth: true,
            },
            component: () => import("@/views/LogoutView.vue"),
        },
        {
            path: "/management/",
            name: "dashboard",
            meta: {
                requireAuth: true,
            },
            component: () => import("@/views/MainView.vue"),
        },
        {
            path: "/",
            redirect: "/management/",
            meta: {
                requireAuth: false,
            },
        },
    ],
});

router.beforeEach((to, from, next) => {
    if (to.name === "logout") {
        authService.logout();
        next({ name: "login" });
    } else if (to.meta.requireAuth && !authService.isLoggedIn()) {
        next({ name: "login" });
    } else {
        next();
    }
});

export default router;
