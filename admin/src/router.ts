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
                    // We don't really need a component here -- just do logout to backend and then redirect.
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
                requireViewPermission: PermissionTarget.EVENT,
            },
            props: true,
            component: () => import("@/views/EventView.vue"),
        },
        {
            path: "/:eventId(\\d+)/blog",
            name: "blog",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.BLOG_ENTRY,
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
    const requireAuth = (to.meta?.requireAuth ?? false) as boolean;
    const viewPerm = to.meta?.requireViewPermission as PermissionTarget | undefined;
    if (requireAuth && !authService.isLoggedIn()) {
        next({ name: "login" });
    } else if (viewPerm && !authService.canView(viewPerm)) {
        next({ name: "index" });
    } else if (to.name === "login" && authService.isLoggedIn()) {
        next({ name: "index" });
    } else {
        next();
    }
});

export default router;
