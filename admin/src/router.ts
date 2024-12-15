import { createRouter, createWebHistory } from "vue-router";

import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";

const authService = useAuth();
const { refreshEvents, getLatestEvent } = useEvents();
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
            path: "/events",
            name: "events",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.EVENT,
            },
            props: true,
            component: () => import("@/views/EventView.vue"),
        },
        {
            path: "/users",
            name: "users",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.USER,
            },
            props: true,
            component: () => import("@/views/UsersView.vue"),
        },
        {
            path: "/:eventId(\\d+)/blog",
            name: "blog",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.BLOG_ENTRY,
            },
            props: true,
            component: () => import("@/views/BlogView.vue"),
        },
        {
            path: "/:eventId(\\d+)/dashboard",
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
            component: {
                async beforeRouteEnter(to, from, next) {
                    // This is the root page. If we end up here, then event has not been selected. Pick one and redirect.
                    // If there are no events created at all, then redirect to events page so that user can create one.
                    await refreshEvents();
                    const event = getLatestEvent();
                    if (event) {
                        next({ name: "dashboard", params: { eventId: event.id } });
                    } else {
                        next({ name: "events" });
                    }
                },
            },
        },
    ],
});

router.beforeEach((to, from, next) => {
    const requireAuth = (to.meta?.requireAuth ?? false) as boolean;
    const viewPerm = to.meta?.requireViewPermission as PermissionTarget | undefined;
    if (requireAuth && !authService.isLoggedIn()) {
        console.debug("Not logged in, redirecting to login page.");
        next({ name: "login" });
    } else if (viewPerm && !authService.canView(viewPerm)) {
        console.debug("No permissions to view, redirecting to index page.");
        next({ name: "index" });
    } else if (to.name === "login" && authService.isLoggedIn()) {
        console.debug("Already logged in, redirecting to index page.");
        next({ name: "index" });
    } else {
        next();
    }
});

export default router;
