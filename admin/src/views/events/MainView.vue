<template>
    <LayoutBase :key="`dashboard-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-row v-if="loading" class="justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-row>

        <template v-else>
            <!-- Event Overview -->
            <v-row class="mb-4">
                <v-col cols="12">
                    <v-card>
                        <v-card-title class="d-flex align-center">
                            <FontAwesomeIcon :icon="faCalendarDays" class="mr-2" />
                            {{ event?.name ?? t("MainView.noEvent") }}
                            <v-chip v-if="event?.archived" class="ml-2" color="grey" size="small">
                                {{ t("MainView.archived") }}
                            </v-chip>
                        </v-card-title>
                        <v-card-text>
                            <div>
                                <span class="text-grey">{{ t("MainView.eventDate") }}:</span>
                                {{ event ? d(event.date, "short") : "-" }}
                            </div>
                            <div v-if="event" class="mt-2">
                                <span class="text-grey">{{ t("MainView.countdown") }}:</span>
                                <EventCountdown :date="event.date" class="ml-1" />
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Statistics Cards -->
            <v-row class="mb-4">
                <v-col v-if="auth.canView(PermissionTarget.BLOG_ENTRY)" cols="12" sm="6" lg>
                    <StatCard
                        :icon="faNewspaper"
                        :value="stats.blogPosts.total"
                        :label="t('MainView.stats.blogPosts')"
                        :subtitle="`${stats.blogPosts.public} ${t('MainView.stats.public')} / ${stats.blogPosts.draft} ${t('MainView.stats.draft')}`"
                        color="blue"
                        clickable
                        @click="router.push({ name: 'blog', params: { eventId } })"
                    />
                </v-col>
                <v-col v-if="auth.canView(PermissionTarget.ENTRY)" cols="12" sm="6" lg>
                    <StatCard
                        :icon="faFilm"
                        :value="stats.compoEntries"
                        :label="t('MainView.stats.compoEntries')"
                        :subtitle="`${stats.compos} ${t('MainView.stats.compos')}`"
                        color="green"
                        clickable
                        @click="router.push({ name: 'entries', params: { eventId } })"
                    />
                </v-col>
                <v-col
                    v-if="auth.canView(PermissionTarget.COMPETITION_PARTICIPATION)"
                    cols="12"
                    sm="6"
                    lg
                >
                    <StatCard
                        :icon="faMedal"
                        :value="stats.competitionParticipants"
                        :label="t('MainView.stats.competitionParticipants')"
                        :subtitle="`${stats.competitions} ${t('MainView.stats.competitions')}`"
                        color="orange"
                        clickable
                        @click="
                            router.push({ name: 'competition-participations', params: { eventId } })
                        "
                    />
                </v-col>
                <v-col v-if="auth.canView(PermissionTarget.STORE_TRANSACTION)" cols="12" sm="6" lg>
                    <StatCard
                        :icon="faCreditCard"
                        :value="stats.transactions.total"
                        :label="t('MainView.stats.transactions')"
                        :subtitle="`${stats.transactions.paid} ${t('MainView.stats.paid')}`"
                        color="teal"
                        clickable
                        @click="router.push({ name: 'store-transactions', params: { eventId } })"
                    />
                </v-col>
                <v-col v-if="auth.canView(PermissionTarget.VOTE_CODE_REQUEST)" cols="12" sm="6" lg>
                    <StatCard
                        :icon="faCheckToSlot"
                        :value="stats.voteCodeRequests.pending"
                        :label="t('MainView.stats.pendingVoteRequests')"
                        :subtitle="`${stats.voteCodeRequests.total} ${t('MainView.stats.totalRequests')}`"
                        color="pink"
                        clickable
                        @click="router.push({ name: 'vote-code-requests', params: { eventId } })"
                    />
                </v-col>
            </v-row>

            <!-- Charts -->
            <v-row class="mb-4">
                <v-col v-if="auth.canView(PermissionTarget.COMPO)" cols="12" md="6">
                    <EntriesPerCompoChart :compos="compos" :entry-counts="compoEntryCounts" />
                </v-col>
                <v-col v-if="auth.canView(PermissionTarget.COMPETITION)" cols="12" md="6">
                    <CompetitionParticipantsChart
                        :competitions="competitions"
                        :participant-counts="competitionParticipantCounts"
                    />
                </v-col>
            </v-row>

            <!-- Recent Activity -->
            <v-row class="mb-4">
                <v-col v-if="auth.canView(PermissionTarget.BLOG_ENTRY)" cols="12" md="6">
                    <v-card>
                        <v-card-title>
                            <FontAwesomeIcon :icon="faClockRotateLeft" class="mr-2" />
                            {{ t("MainView.recentActivity.blogPosts") }}
                        </v-card-title>
                        <v-card-text>
                            <v-list v-if="recentBlogPosts.length > 0" density="compact">
                                <v-list-item
                                    v-for="post in recentBlogPosts"
                                    :key="post.id"
                                    :title="post.title"
                                    :subtitle="d(post.date, 'long')"
                                >
                                    <template #prepend>
                                        <FontAwesomeIcon
                                            :icon="post.public ? faEye : faEyeSlash"
                                            :class="
                                                post.public ? 'text-green mr-3' : 'text-grey mr-3'
                                            "
                                            size="sm"
                                        />
                                    </template>
                                </v-list-item>
                            </v-list>
                            <div v-else class="text-center text-grey py-4">
                                {{ t("MainView.recentActivity.noRecentPosts") }}
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col v-if="auth.canView(PermissionTarget.ENTRY)" cols="12" md="6">
                    <v-card>
                        <v-card-title>
                            <FontAwesomeIcon :icon="faFileImport" class="mr-2" />
                            {{ t("MainView.recentActivity.compoEntries") }}
                        </v-card-title>
                        <v-card-text>
                            <v-list v-if="recentCompoEntries.length > 0" density="compact">
                                <v-list-item
                                    v-for="entry in recentCompoEntries"
                                    :key="entry.id"
                                    :title="entry.name"
                                    :subtitle="getCompoName(entry.compo)"
                                >
                                    <template #prepend>
                                        <FontAwesomeIcon :icon="faFile" size="sm" class="mr-3" />
                                    </template>
                                </v-list-item>
                            </v-list>
                            <div v-else class="text-center text-grey py-4">
                                {{ t("MainView.recentActivity.noRecentEntries") }}
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </template>
    </LayoutBase>
</template>

<script setup lang="ts">
import { parseInt } from "lodash-es";
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import {
    faCalendarDays,
    faCheckToSlot,
    faClockRotateLeft,
    faCreditCard,
    faEye,
    faEyeSlash,
    faFile,
    faFileImport,
    faFilm,
    faMedal,
    faNewspaper,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { useRouter } from "vue-router";

import * as api from "@/api";
import type { BlogEntry, Compo, CompoEntry, Competition, Event } from "@/api";
import CompetitionParticipantsChart from "@/components/dashboard/charts/CompetitionParticipantsChart.vue";
import EntriesPerCompoChart from "@/components/dashboard/charts/EntriesPerCompoChart.vue";
import EventCountdown from "@/components/dashboard/EventCountdown.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import StatCard from "@/components/dashboard/StatCard.vue";
import { PermissionTarget, useAuth } from "@/services/auth";

const router = useRouter();

const props = defineProps<{ eventId: string }>();
const { t, d } = useI18n();
const auth = useAuth();

const loading = ref(true);
const event = ref<Event | null>(null);
const eventIdNum = computed(() => parseInt(props.eventId, 10));

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: event.value?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    { title: t("MainView.title"), disabled: true },
]);

// Statistics
const stats = ref({
    blogPosts: { total: 0, public: 0, draft: 0 },
    compoEntries: 0,
    compos: 0,
    competitionParticipants: 0,
    competitions: 0,
    transactions: { total: 0, paid: 0 },
    voteCodeRequests: { total: 0, pending: 0 },
});

// Recent activity
const recentBlogPosts = ref<BlogEntry[]>([]);
const recentCompoEntries = ref<CompoEntry[]>([]);
// Chart data
const compos = ref<Compo[]>([]);
const competitions = ref<Competition[]>([]);
const compoEntryCounts = ref<Map<number, number>>(new Map());
const competitionParticipantCounts = ref<Map<number, number>>(new Map());

function getCompoName(compoId: number): string {
    return compos.value.find((c) => c.id === compoId)?.name ?? t("MainView.unknown");
}

async function loadEvent(eid: number) {
    try {
        const response = await api.adminEventsRetrieve({ path: { id: eid } });
        event.value = response.data ?? null;
    } catch (e) {
        console.error("Failed to load event:", e);
    }
}

async function loadBlogPosts(eid: number) {
    if (!auth.canView(PermissionTarget.BLOG_ENTRY)) return;
    try {
        const response = await api.adminBlogList({ query: { event: eid, limit: 1000 } });
        const blogPosts = response.data?.results ?? [];
        const publicPosts = blogPosts.filter((p) => p.public).length;
        stats.value.blogPosts = {
            total: blogPosts.length,
            public: publicPosts,
            draft: blogPosts.length - publicPosts,
        };
        recentBlogPosts.value = blogPosts.slice(0, 5);
    } catch (e) {
        console.error("Failed to load blog posts:", e);
    }
}

async function loadComposAndEntries(eid: number) {
    if (!auth.canView(PermissionTarget.COMPO) && !auth.canView(PermissionTarget.ENTRY)) return;
    try {
        const [compoResponse, entriesResponse] = await Promise.all([
            api.adminEventKompomaattiComposList({
                path: { event_pk: eid },
                query: { limit: 1000 },
            }),
            api.adminEventKompomaattiEntriesList({
                path: { event_pk: eid },
                query: { limit: 1000 },
            }),
        ]);

        const compoList = compoResponse.data?.results ?? [];
        const entries = entriesResponse.data?.results ?? [];
        compos.value = compoList;
        stats.value.compos = compoList.length;
        stats.value.compoEntries = entries.length;
        recentCompoEntries.value = entries.slice(0, 5);

        const entryCounts = new Map<number, number>();
        for (const entry of entries) {
            entryCounts.set(entry.compo, (entryCounts.get(entry.compo) ?? 0) + 1);
        }
        compoEntryCounts.value = entryCounts;
    } catch (e) {
        console.error("Failed to load compos/entries:", e);
    }
}

async function loadCompetitionsAndParticipants(eid: number) {
    if (!auth.canView(PermissionTarget.COMPETITION) && !auth.canView(PermissionTarget.COMPETITION_PARTICIPATION)) {
        return;
    }
    try {
        const [competitionsResponse, participantsResponse] = await Promise.all([
            api.adminEventKompomaattiCompetitionsList({
                path: { event_pk: eid },
                query: { limit: 1000 },
            }),
            api.adminEventKompomaattiCompetitionParticipationsList({
                path: { event_pk: eid },
                query: { limit: 1000 },
            }),
        ]);

        const competitionList = competitionsResponse.data?.results ?? [];
        const participants = participantsResponse.data?.results ?? [];
        competitions.value = competitionList;
        stats.value.competitions = competitionList.length;
        stats.value.competitionParticipants = participants.length;

        const participantCounts = new Map<number, number>();
        for (const p of participants) {
            participantCounts.set(p.competition, (participantCounts.get(p.competition) ?? 0) + 1);
        }
        competitionParticipantCounts.value = participantCounts;
    } catch (e) {
        console.error("Failed to load competitions/participants:", e);
    }
}

async function loadTransactions(eid: number) {
    if (!auth.canView(PermissionTarget.STORE_TRANSACTION)) return;
    try {
        const response = await api.adminEventStoreTransactionsList({
            path: { event_pk: eid },
            query: { limit: 1000 },
        });
        const transactions = response.data?.results ?? [];
        const paidTransactions = transactions.filter((tx) => tx.time_paid).length;
        stats.value.transactions = {
            total: transactions.length,
            paid: paidTransactions,
        };
    } catch (e) {
        console.error("Failed to load transactions:", e);
    }
}

async function loadVoteCodeRequests(eid: number) {
    if (!auth.canView(PermissionTarget.VOTE_CODE_REQUEST)) return;
    try {
        const response = await api.adminEventKompomaattiVoteCodeRequestsList({
            path: { event_pk: eid },
            query: { limit: 1000 },
        });
        const voteRequests = response.data?.results ?? [];
        const pendingRequests = voteRequests.filter((r) => r.status === 0).length;
        stats.value.voteCodeRequests = {
            total: voteRequests.length,
            pending: pendingRequests,
        };
    } catch (e) {
        console.error("Failed to load vote code requests:", e);
    }
}

async function loadDashboardData() {
    loading.value = true;
    const eid = eventIdNum.value;

    await loadEvent(eid);
    await Promise.all([
        loadBlogPosts(eid),
        loadComposAndEntries(eid),
        loadCompetitionsAndParticipants(eid),
        loadTransactions(eid),
        loadVoteCodeRequests(eid),
    ]);

    loading.value = false;
}

onMounted(loadDashboardData);
watch(() => props.eventId, loadDashboardData);
</script>
