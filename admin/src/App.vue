<template>
    <v-app>
        <Navigation
            v-if="authService.isLoggedIn()"
            :primary="primaryLinks"
            :secondary="secondaryLinks"
        />
        <v-main :class="backgroundClass">
            <RouterView />
            <ConfirmDialog ref="confirmDialog" />
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import {
    faArchive,
    faBlog,
    faBoxes,
    faBoxOpen,
    faCalendarAlt,
    faChartPie,
    faClockRotateLeft,
    faCreditCard,
    faDashboard,
    faEnvelope,
    faFileAudio,
    faFolder,
    faGamepad,
    faKey,
    faMusic,
    faNewspaper,
    faPeopleGroup,
    faReceipt,
    faRightFromBracket,
    faStore,
    faTicket,
    faTrophy,
    faUpload,
    faUsers,
    faVideo,
} from "@fortawesome/free-solid-svg-icons";
import { computed, provide, ref } from "vue";
import { useI18n } from "vue-i18n";

import ConfirmDialog from "@/components/dialogs/ConfirmDialog.vue";
import Navigation from "@/components/layout/MainNavigation.vue";
import type { NavigationLinks } from "@/components/layout/NavigationList.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { confirmDialogKey } from "@/symbols";

const { t } = useI18n();
const backgroundClass = computed(() => (authService.isLoggedIn() ? "main-view" : "login-view"));
const authService = useAuth();
const confirmDialog = ref(undefined);
const primaryLinks = computed(
    (): NavigationLinks => [
        {
            title: t("App.nav.dashboard"),
            icon: faDashboard,
            to: "dashboard",
        },
        {
            title: t("App.nav.content"),
            icon: faNewspaper,
            children: [
                {
                    title: t("App.nav.blog"),
                    icon: faBlog,
                    to: "blog",
                    requirePerm: PermissionTarget.BLOG_ENTRY,
                },
                {
                    title: t("App.nav.program"),
                    icon: faCalendarAlt,
                    to: "program",
                    requirePerm: PermissionTarget.PROGRAMME_EVENT,
                },
                {
                    title: t("App.nav.uploads"),
                    icon: faUpload,
                    to: "uploads",
                    requirePerm: PermissionTarget.UPLOADED_FILE,
                },
            ],
        },
        {
            title: t("App.nav.kompomaatti"),
            icon: faTrophy,
            children: [
                {
                    title: t("App.nav.compos"),
                    icon: faMusic,
                    to: "compos",
                    requirePerm: PermissionTarget.COMPO,
                },
                {
                    title: t("App.nav.entries"),
                    icon: faFileAudio,
                    to: "entries",
                    requirePerm: PermissionTarget.ENTRY,
                },
                {
                    title: t("App.nav.competitions"),
                    icon: faGamepad,
                    to: "competitions",
                    requirePerm: PermissionTarget.COMPETITION,
                },
                {
                    title: t("App.nav.competitionParticipations"),
                    icon: faPeopleGroup,
                    to: "competition-participations",
                    requirePerm: PermissionTarget.COMPETITION_PARTICIPATION,
                },
                {
                    title: t("App.nav.voteCodes"),
                    icon: faTicket,
                    to: "vote-codes",
                    requirePerm: PermissionTarget.TICKET_VOTE_CODE,
                },
                {
                    title: t("App.nav.voteCodeRequests"),
                    icon: faEnvelope,
                    to: "vote-code-requests",
                    requirePerm: PermissionTarget.VOTE_CODE_REQUEST,
                },
            ],
        },
        {
            title: t("App.nav.store"),
            icon: faStore,
            children: [
                {
                    title: t("App.nav.storeSummary"),
                    icon: faChartPie,
                    to: "store-summary",
                    requirePerm: PermissionTarget.STORE_ITEM,
                },
                {
                    title: t("App.nav.storeItems"),
                    icon: faBoxOpen,
                    to: "store-items",
                    requirePerm: PermissionTarget.STORE_ITEM,
                },
                {
                    title: t("App.nav.transactions"),
                    icon: faCreditCard,
                    to: "store-transactions",
                    requirePerm: PermissionTarget.STORE_TRANSACTION,
                },
                {
                    title: t("App.nav.transactionItems"),
                    icon: faReceipt,
                    to: "store-transaction-items",
                    requirePerm: PermissionTarget.TRANSACTION_ITEM,
                },
            ],
        },
        {
            title: t("App.nav.arkisto"),
            icon: faArchive,
            children: [
                {
                    title: t("App.nav.arkistoArchiver"),
                    icon: faBoxes,
                    to: "arkisto-archiver",
                    requirePerm: PermissionTarget.ENTRY,
                },
                {
                    title: t("App.nav.arkistoCategories"),
                    icon: faFolder,
                    to: "arkisto-categories",
                    requirePerm: PermissionTarget.OTHER_VIDEO_CATEGORY,
                },
                {
                    title: t("App.nav.arkistoVideos"),
                    icon: faVideo,
                    to: "arkisto-videos",
                    requirePerm: PermissionTarget.OTHER_VIDEO,
                },
            ],
        },
    ]
);
const secondaryLinks = computed(
    (): NavigationLinks => [
        {
            title: t("App.nav.users"),
            icon: faUsers,
            to: "users",
            noEventId: true,
        },
        {
            title: t("App.nav.apiTokens"),
            icon: faKey,
            to: "tokens",
            noEventId: true,
            requirePerm: PermissionTarget.AUTH_TOKEN,
        },
        {
            title: t("App.nav.auditLog"),
            icon: faClockRotateLeft,
            to: "auditlog",
            noEventId: true,
            requirePerm: PermissionTarget.LOG_ENTRY,
        },
        {
            title: t("App.nav.logout"),
            icon: faRightFromBracket,
            to: "logout",
            noEventId: true,
        },
    ]
);

provide(confirmDialogKey, confirmDialog);
</script>

<style scoped lang="scss">
.login-view {
    background-image: url("@/assets/webtausta.jpg");
    background-repeat: no-repeat;
    background-size: cover;
}

.main-view {
    background-image:
        linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)),
        url("@/assets/webtausta.jpg");
    background-repeat: no-repeat;
    background-size: cover;
    background-attachment: fixed;
}
</style>
