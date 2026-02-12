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
            component: () => import("@/views/auth/LoginView.vue"),
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
            component: () => import("@/views/events/EventEditView.vue"),
        },
        {
            path: "/events/:id(\\d+)/edit",
            name: "events-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.EVENT,
            },
            props: true,
            component: () => import("@/views/events/EventEditView.vue"),
        },
        {
            path: "/events",
            name: "events",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.EVENT,
            },
            props: true,
            component: () => import("@/views/events/EventView.vue"),
        },
        {
            path: "/users/new",
            name: "users-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.USER,
            },
            props: true,
            component: () => import("@/views/users/UserEditView.vue"),
        },
        {
            path: "/users/:id(\\d+)/edit",
            name: "users-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.USER,
            },
            props: true,
            component: () => import("@/views/users/UserEditView.vue"),
        },
        {
            path: "/users",
            name: "users",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.USER,
            },
            props: true,
            component: () => import("@/views/users/UsersView.vue"),
        },
        {
            path: "/profile",
            name: "profile",
            meta: {
                requireAuth: true,
            },
            component: () => import("@/views/profile/ProfileView.vue"),
        },
        {
            path: "/tokens",
            name: "tokens",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.AUTH_TOKEN,
            },
            component: () => import("@/views/tokens/TokensView.vue"),
        },
        {
            path: "/auditlog",
            name: "auditlog",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.LOG_ENTRY,
            },
            component: () => import("@/views/auditlog/AuditLogView.vue"),
        },
        {
            path: "/:eventId(\\d+)/blog/new",
            name: "blog-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.BLOG_ENTRY,
            },
            props: true,
            component: () => import("@/views/blog/BlogEntryEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/blog/:id(\\d+)/edit",
            name: "blog-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.BLOG_ENTRY,
            },
            props: true,
            component: () => import("@/views/blog/BlogEntryEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/blog",
            name: "blog",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.BLOG_ENTRY,
            },
            props: true,
            component: () => import("@/views/blog/BlogView.vue"),
        },
        // Program Events
        {
            path: "/:eventId(\\d+)/program",
            name: "program",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.PROGRAMME_EVENT,
            },
            props: true,
            component: () => import("@/views/program/ProgramEventsView.vue"),
        },
        {
            path: "/:eventId(\\d+)/program/new",
            name: "program-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.PROGRAMME_EVENT,
            },
            props: true,
            component: () => import("@/views/program/ProgramEventEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/program/:id(\\d+)/edit",
            name: "program-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.PROGRAMME_EVENT,
            },
            props: true,
            component: () => import("@/views/program/ProgramEventEditView.vue"),
        },
        // Uploads
        {
            path: "/:eventId(\\d+)/uploads",
            name: "uploads",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.UPLOADED_FILE,
            },
            props: true,
            component: () => import("@/views/uploads/UploadsView.vue"),
        },
        {
            path: "/:eventId(\\d+)/uploads/new",
            name: "uploads-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.UPLOADED_FILE,
            },
            props: true,
            component: () => import("@/views/uploads/UploadEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/uploads/:id(\\d+)/edit",
            name: "uploads-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.UPLOADED_FILE,
            },
            props: true,
            component: () => import("@/views/uploads/UploadEditView.vue"),
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
            component: () => import("@/views/kompomaatti/ComposView.vue"),
        },
        {
            path: "/:eventId(\\d+)/compos/new",
            name: "compos-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPO,
            },
            props: true,
            component: () => import("@/views/kompomaatti/CompoEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/compos/:id(\\d+)/edit",
            name: "compos-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPO,
            },
            props: true,
            component: () => import("@/views/kompomaatti/CompoEditView.vue"),
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
            component: () => import("@/views/kompomaatti/EntriesView.vue"),
        },
        {
            path: "/:eventId(\\d+)/entries/new",
            name: "entries-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.ENTRY,
            },
            props: true,
            component: () => import("@/views/kompomaatti/EntryEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/entries/:id(\\d+)/edit",
            name: "entries-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.ENTRY,
            },
            props: true,
            component: () => import("@/views/kompomaatti/EntryEditView.vue"),
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
            component: () => import("@/views/kompomaatti/CompetitionsView.vue"),
        },
        {
            path: "/:eventId(\\d+)/competitions/new",
            name: "competitions-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPETITION,
            },
            props: true,
            component: () => import("@/views/kompomaatti/CompetitionEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/competitions/:id(\\d+)/edit",
            name: "competitions-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPETITION,
            },
            props: true,
            component: () => import("@/views/kompomaatti/CompetitionEditView.vue"),
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
            component: () => import("@/views/kompomaatti/CompetitionParticipationsView.vue"),
        },
        {
            path: "/:eventId(\\d+)/competition-participations/new",
            name: "competition-participations-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPETITION_PARTICIPATION,
            },
            props: true,
            component: () => import("@/views/kompomaatti/CompetitionParticipationEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/competition-participations/:id(\\d+)/edit",
            name: "competition-participations-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.COMPETITION_PARTICIPATION,
            },
            props: true,
            component: () => import("@/views/kompomaatti/CompetitionParticipationEditView.vue"),
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
            component: () => import("@/views/kompomaatti/VoteCodesView.vue"),
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
            component: () => import("@/views/kompomaatti/VoteCodeRequestsView.vue"),
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
            component: () => import("@/views/store/StoreItemsView.vue"),
        },
        {
            path: "/:eventId(\\d+)/store/items/new",
            name: "store-items-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.STORE_ITEM,
            },
            props: true,
            component: () => import("@/views/store/StoreItemEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/store/items/:id(\\d+)/edit",
            name: "store-items-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.STORE_ITEM,
            },
            props: true,
            component: () => import("@/views/store/StoreItemEditView.vue"),
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
            component: () => import("@/views/store/TransactionsView.vue"),
        },
        {
            path: "/:eventId(\\d+)/store/transactions/:id(\\d+)",
            name: "store-transaction-detail",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.STORE_TRANSACTION,
            },
            props: true,
            component: () => import("@/views/store/TransactionDetailView.vue"),
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
            component: () => import("@/views/store/TransactionItemsView.vue"),
        },
        // Store Summary
        {
            path: "/:eventId(\\d+)/store/summary",
            name: "store-summary",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.STORE_ITEM,
            },
            props: true,
            component: () => import("@/views/store/StoreSummaryView.vue"),
        },
        // Arkisto (Archive) - Video Categories
        {
            path: "/:eventId(\\d+)/arkisto/categories",
            name: "arkisto-categories",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.OTHER_VIDEO_CATEGORY,
            },
            props: true,
            component: () => import("@/views/arkisto/VideoCategoriesView.vue"),
        },
        {
            path: "/:eventId(\\d+)/arkisto/categories/new",
            name: "arkisto-categories-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.OTHER_VIDEO_CATEGORY,
            },
            props: true,
            component: () => import("@/views/arkisto/VideoCategoryEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/arkisto/categories/:id(\\d+)/edit",
            name: "arkisto-categories-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.OTHER_VIDEO_CATEGORY,
            },
            props: true,
            component: () => import("@/views/arkisto/VideoCategoryEditView.vue"),
        },
        // Arkisto (Archive) - Videos
        {
            path: "/:eventId(\\d+)/arkisto/videos",
            name: "arkisto-videos",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.OTHER_VIDEO,
            },
            props: true,
            component: () => import("@/views/arkisto/VideosView.vue"),
        },
        {
            path: "/:eventId(\\d+)/arkisto/videos/new",
            name: "arkisto-videos-new",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.OTHER_VIDEO,
            },
            props: true,
            component: () => import("@/views/arkisto/VideoEditView.vue"),
        },
        {
            path: "/:eventId(\\d+)/arkisto/videos/:id(\\d+)/edit",
            name: "arkisto-videos-edit",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.OTHER_VIDEO,
            },
            props: true,
            component: () => import("@/views/arkisto/VideoEditView.vue"),
        },
        // Arkisto (Archive) - Archiver
        {
            path: "/:eventId(\\d+)/arkisto/archiver",
            name: "arkisto-archiver",
            meta: {
                requireAuth: true,
                requireViewPermission: PermissionTarget.ENTRY,
            },
            props: true,
            component: () => import("@/views/arkisto/ArchiverView.vue"),
        },
        {
            path: "/:eventId(\\d+)/dashboard",
            name: "dashboard",
            meta: {
                requireAuth: true,
            },
            props: true,
            component: () => import("@/views/events/MainView.vue"),
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
