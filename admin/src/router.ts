import { createRouter, createWebHistory } from "vue-router";

import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { HttpStatus, isHttpError } from "@/utils/http_status";

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
                    try {
                        await authService.logout();
                    } catch (e) {
                        console.error("Logout failed:", e);
                    }
                    next({ name: "login" });
                },
            },
        },
        {
            path: "/events/new",
            name: "events-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.EVENT,
            },
            props: true,
            component: () => import("@/views/EventEditView.vue"),
        },
        {
            path: "/events/:id(\\d+)/edit",
            name: "events-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.EVENT,
            },
            props: true,
            component: () => import("@/views/EventEditView.vue"),
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
            path: "/users/new",
            name: "users-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.USER,
            },
            props: true,
            component: () => import("@/views/UserEditView.vue"),
        },
        {
            path: "/users/:id(\\d+)/edit",
            name: "users-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.USER,
            },
            props: true,
            component: () => import("@/views/UserEditView.vue"),
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
            path: "/:eventId(\\d+)/blog/new",
            name: "blog-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.BLOG_ENTRY,
            },
            props: true,
            component: () => import("@/views/BlogEntryEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/blog/:id(\\d+)/edit",
            name: "blog-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.BLOG_ENTRY,
            },
            props: true,
            component: () => import("@/views/BlogEntryEditView.vue"),
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
        // Compos
        {
            path: "/:eventId(\\d+)/compos",
            name: "compos",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPO,
            },
            props: true,
            component: () => import("@/views/ComposView.vue"),
        },
        {
            path: "/:eventId(\\d+)/compos/new",
            name: "compos-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPO,
            },
            props: true,
            component: () => import("@/views/CompoEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/compos/:id(\\d+)/edit",
            name: "compos-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPO,
            },
            props: true,
            component: () => import("@/views/CompoEditView.vue"),
        },
        // Entries
        {
            path: "/:eventId(\\d+)/entries",
            name: "entries",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.ENTRY,
            },
            props: true,
            component: () => import("@/views/EntriesView.vue"),
        },
        {
            path: "/:eventId(\\d+)/entries/new",
            name: "entries-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.ENTRY,
            },
            props: true,
            component: () => import("@/views/EntryEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/entries/:id(\\d+)/edit",
            name: "entries-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.ENTRY,
            },
            props: true,
            component: () => import("@/views/EntryEditView.vue"),
        },
        // Competitions
        {
            path: "/:eventId(\\d+)/competitions",
            name: "competitions",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPETITION,
            },
            props: true,
            component: () => import("@/views/CompetitionsView.vue"),
        },
        {
            path: "/:eventId(\\d+)/competitions/new",
            name: "competitions-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPETITION,
            },
            props: true,
            component: () => import("@/views/CompetitionEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/competitions/:id(\\d+)/edit",
            name: "competitions-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPETITION,
            },
            props: true,
            component: () => import("@/views/CompetitionEditView.vue"),
        },
        // Competition Participations
        {
            path: "/:eventId(\\d+)/competition-participations",
            name: "competition-participations",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPETITION_PARTICIPATION,
            },
            props: true,
            component: () => import("@/views/CompetitionParticipationsView.vue"),
        },
        {
            path: "/:eventId(\\d+)/competition-participations/new",
            name: "competition-participations-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPETITION_PARTICIPATION,
            },
            props: true,
            component: () => import("@/views/CompetitionParticipationEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/competition-participations/:id(\\d+)/edit",
            name: "competition-participations-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPETITION_PARTICIPATION,
            },
            props: true,
            component: () => import("@/views/CompetitionParticipationEditView.vue"),
        },
        // Vote Codes
        {
            path: "/:eventId(\\d+)/vote-codes",
            name: "vote-codes",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.TICKET_VOTE_CODE,
            },
            props: true,
            component: () => import("@/views/VoteCodesView.vue"),
        },
        // Vote Code Requests
        {
            path: "/:eventId(\\d+)/vote-code-requests",
            name: "vote-code-requests",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.VOTE_CODE_REQUEST,
            },
            props: true,
            component: () => import("@/views/VoteCodeRequestsView.vue"),
        },
        // Store Items
        {
            path: "/:eventId(\\d+)/store/items",
            name: "store-items",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.STORE_ITEM,
            },
            props: true,
            component: () => import("@/views/StoreItemsView.vue"),
        },
        {
            path: "/:eventId(\\d+)/store/items/new",
            name: "store-items-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.STORE_ITEM,
            },
            props: true,
            component: () => import("@/views/StoreItemEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/store/items/:id(\\d+)/edit",
            name: "store-items-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.STORE_ITEM,
            },
            props: true,
            component: () => import("@/views/StoreItemEditView.vue"),
        },
        // Transactions
        {
            path: "/:eventId(\\d+)/store/transactions",
            name: "store-transactions",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.STORE_TRANSACTION,
            },
            props: true,
            component: () => import("@/views/TransactionsView.vue"),
        },
        {
            path: "/:eventId(\\d+)/store/transactions/:id(\\d+)",
            name: "store-transaction-detail",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.STORE_TRANSACTION,
            },
            props: true,
            component: () => import("@/views/TransactionDetailView.vue"),
        },
        // Transaction Items
        {
            path: "/:eventId(\\d+)/store/transaction-items",
            name: "store-transaction-items",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.TRANSACTION_ITEM,
            },
            props: true,
            component: () => import("@/views/TransactionItemsView.vue"),
        },
        // Store Summary
        {
            path: "/:eventId(\\d+)/store/summary",
            name: "store-summary",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.TRANSACTION_ITEM,
            },
            props: true,
            component: () => import("@/views/StoreSummaryView.vue"),
        },
        {
            path: "/:eventId(\\d+)/dashboard",
            name: "dashboard",
            meta: {
                requireAuth: true,
            },
            props: true,
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
                    try {
                        await refreshEvents();
                    } catch (e) {
                        if (isHttpError(e, HttpStatus.FORBIDDEN)) {
                            console.error("Permission denied, logging out");
                            await authService.logout();
                            next({ name: "login" });
                            return;
                        }
                        console.error("Failed to refresh events:", e);
                    }
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
