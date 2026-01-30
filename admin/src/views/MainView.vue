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
                                {{ event ? d(event.date, "long") : "-" }}
                            </div>
                            <div v-if="event" class="mt-2">
                                <span class="text-grey">{{ t("MainView.countdown") }}:</span>
                                <v-chip :color="countdownColor" size="small" class="ml-1">
                                    {{ countdownText }}
                                </v-chip>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Statistics Cards -->
            <v-row class="mb-4">
                <v-col v-if="auth.canView(PermissionTarget.BLOG_ENTRY)" cols="12" sm="6" lg>
                    <v-card
                        color="blue"
                        variant="tonal"
                        class="cursor-pointer"
                        @click="router.push({ name: 'blog', params: { eventId } })"
                    >
                        <v-card-text class="d-flex align-center">
                            <FontAwesomeIcon :icon="faNewspaper" size="2x" class="mr-4" />
                            <div>
                                <div class="text-h4">{{ stats.blogPosts.total }}</div>
                                <div class="text-body-2">{{ t("MainView.stats.blogPosts") }}</div>
                                <div class="text-caption text-grey">
                                    {{ stats.blogPosts.public }} {{ t("MainView.stats.public") }} /
                                    {{ stats.blogPosts.draft }} {{ t("MainView.stats.draft") }}
                                </div>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col v-if="auth.canView(PermissionTarget.ENTRY)" cols="12" sm="6" lg>
                    <v-card
                        color="green"
                        variant="tonal"
                        class="cursor-pointer"
                        @click="router.push({ name: 'entries', params: { eventId } })"
                    >
                        <v-card-text class="d-flex align-center">
                            <FontAwesomeIcon :icon="faFilm" size="2x" class="mr-4" />
                            <div>
                                <div class="text-h4">{{ stats.compoEntries }}</div>
                                <div class="text-body-2">
                                    {{ t("MainView.stats.compoEntries") }}
                                </div>
                                <div class="text-caption text-grey">
                                    {{ stats.compos }} {{ t("MainView.stats.compos") }}
                                </div>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col
                    v-if="auth.canView(PermissionTarget.COMPETITION_PARTICIPATION)"
                    cols="12"
                    sm="6"
                    lg
                >
                    <v-card
                        color="orange"
                        variant="tonal"
                        class="cursor-pointer"
                        @click="
                            router.push({ name: 'competition-participations', params: { eventId } })
                        "
                    >
                        <v-card-text class="d-flex align-center">
                            <FontAwesomeIcon :icon="faMedal" size="2x" class="mr-4" />
                            <div>
                                <div class="text-h4">{{ stats.competitionParticipants }}</div>
                                <div class="text-body-2">
                                    {{ t("MainView.stats.competitionParticipants") }}
                                </div>
                                <div class="text-caption text-grey">
                                    {{ stats.competitions }} {{ t("MainView.stats.competitions") }}
                                </div>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col v-if="auth.canView(PermissionTarget.STORE_TRANSACTION)" cols="12" sm="6" lg>
                    <v-card
                        color="teal"
                        variant="tonal"
                        class="cursor-pointer"
                        @click="router.push({ name: 'store-transactions', params: { eventId } })"
                    >
                        <v-card-text class="d-flex align-center">
                            <FontAwesomeIcon :icon="faCreditCard" size="2x" class="mr-4" />
                            <div>
                                <div class="text-h4">{{ stats.transactions.total }}</div>
                                <div class="text-body-2">
                                    {{ t("MainView.stats.transactions") }}
                                </div>
                                <div class="text-caption text-grey">
                                    {{ stats.transactions.paid }} {{ t("MainView.stats.paid") }}
                                </div>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col v-if="auth.canView(PermissionTarget.VOTE_CODE_REQUEST)" cols="12" sm="6" lg>
                    <v-card
                        color="pink"
                        variant="tonal"
                        class="cursor-pointer"
                        @click="router.push({ name: 'vote-code-requests', params: { eventId } })"
                    >
                        <v-card-text class="d-flex align-center">
                            <FontAwesomeIcon :icon="faCheckToSlot" size="2x" class="mr-4" />
                            <div>
                                <div class="text-h4">{{ stats.voteCodeRequests.pending }}</div>
                                <div class="text-body-2">
                                    {{ t("MainView.stats.pendingVoteRequests") }}
                                </div>
                                <div class="text-caption text-grey">
                                    {{ stats.voteCodeRequests.total }}
                                    {{ t("MainView.stats.totalRequests") }}
                                </div>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Charts -->
            <v-row class="mb-4">
                <v-col v-if="auth.canView(PermissionTarget.COMPO)" cols="12" md="6">
                    <v-card>
                        <v-card-title>
                            <FontAwesomeIcon :icon="faChartPie" class="mr-2" />
                            {{ t("MainView.charts.entriesPerCompo") }}
                        </v-card-title>
                        <v-card-text>
                            <div v-if="compoChartData.labels.length > 0" style="height: 300px">
                                <Pie :data="compoChartData" :options="pieChartOptions" />
                            </div>
                            <div v-else class="text-center text-grey py-8">
                                {{ t("MainView.charts.noData") }}
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col v-if="auth.canView(PermissionTarget.COMPETITION)" cols="12" md="6">
                    <v-card>
                        <v-card-title>
                            <FontAwesomeIcon :icon="faChartBar" class="mr-2" />
                            {{ t("MainView.charts.competitionParticipants") }}
                        </v-card-title>
                        <v-card-text>
                            <div
                                v-if="competitionChartData.labels.length > 0"
                                style="height: 300px"
                            >
                                <Bar :data="competitionChartData" :options="barChartOptions" />
                            </div>
                            <div v-else class="text-center text-grey py-8">
                                {{ t("MainView.charts.noData") }}
                            </div>
                        </v-card-text>
                    </v-card>
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
import {
    ArcElement,
    BarElement,
    CategoryScale,
    Chart as ChartJS,
    Legend,
    LinearScale,
    Title,
    Tooltip,
} from "chart.js";
import { parseInt } from "lodash-es";
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { Bar, Pie } from "vue-chartjs";
import {
    faCalendarDays,
    faChartBar,
    faChartPie,
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
import LayoutBase, { type BreadcrumbItem } from "@/components/LayoutBase.vue";
import { PermissionTarget, useAuth } from "@/services/auth";

const router = useRouter();

// Register Chart.js components
ChartJS.register(ArcElement, BarElement, CategoryScale, Legend, LinearScale, Title, Tooltip);

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

// Countdown
const countdownDays = computed(() => {
    if (!event.value) return 0;
    const eventDate = new Date(event.value.date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    eventDate.setHours(0, 0, 0, 0);
    return Math.ceil((eventDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
});

const countdownText = computed(() => {
    const days = countdownDays.value;
    if (days > 0) {
        return t("MainView.daysUntil", { days });
    } else if (days === 0) {
        return t("MainView.today");
    } else {
        return t("MainView.daysAgo", { days: Math.abs(days) });
    }
});

const countdownColor = computed(() => {
    const days = countdownDays.value;
    if (days > 7) return "green";
    if (days > 0) return "orange";
    if (days === 0) return "red";
    return "grey";
});

// Chart configurations
const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: "right" as const,
        },
    },
};

const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false,
        },
    },
    scales: {
        y: {
            beginAtZero: true,
            ticks: {
                stepSize: 1,
            },
        },
    },
};

const chartColors = [
    "#4CAF50",
    "#2196F3",
    "#FF9800",
    "#9C27B0",
    "#E91E63",
    "#00BCD4",
    "#FFEB3B",
    "#795548",
    "#607D8B",
    "#F44336",
];

const compoChartData = computed(() => ({
    labels: compos.value.map((c) => c.name),
    datasets: [
        {
            data: compos.value.map((c) => compoEntryCounts.value.get(c.id) ?? 0),
            backgroundColor: chartColors.slice(0, compos.value.length),
        },
    ],
}));

const competitionChartData = computed(() => ({
    labels: competitions.value.map((c) => c.name),
    datasets: [
        {
            label: t("MainView.stats.participants"),
            data: competitions.value.map((c) => competitionParticipantCounts.value.get(c.id) ?? 0),
            backgroundColor: "#2196F3",
        },
    ],
}));

function getCompoName(compoId: number): string {
    return compos.value.find((c) => c.id === compoId)?.name ?? t("MainView.unknown");
}

async function loadDashboardData() {
    loading.value = true;
    const eid = eventIdNum.value;

    try {
        // Load event details
        const eventResponse = await api.adminEventsRetrieve({ path: { id: eid } });
        event.value = eventResponse.data ?? null;

        // Load all data in parallel
        const [
            blogResponse,
            compoResponse,
            entriesResponse,
            competitionsResponse,
            participantsResponse,
            transactionsResponse,
            voteRequestsResponse,
        ] = await Promise.all([
            api.adminBlogList({ query: { event: eid, limit: 1000 } }),
            api.adminEventKompomaattiComposList({
                path: { event_pk: eid },
                query: { limit: 1000 },
            }),
            api.adminEventKompomaattiEntriesList({
                path: { event_pk: eid },
                query: { limit: 1000 },
            }),
            api.adminEventKompomaattiCompetitionsList({
                path: { event_pk: eid },
                query: { limit: 1000 },
            }),
            api.adminEventKompomaattiCompetitionParticipationsList({
                path: { event_pk: eid },
                query: { limit: 1000 },
            }),
            api.adminEventStoreTransactionsList({
                path: { event_pk: eid },
                query: { limit: 1000 },
            }),
            api.adminEventKompomaattiVoteCodeRequestsList({
                path: { event_pk: eid },
                query: { limit: 1000 },
            }),
        ]);

        // Process blog stats
        const blogPosts = blogResponse.data?.results ?? [];
        const publicPosts = blogPosts.filter((p) => p.public).length;
        stats.value.blogPosts = {
            total: blogPosts.length,
            public: publicPosts,
            draft: blogPosts.length - publicPosts,
        };
        recentBlogPosts.value = blogPosts.slice(0, 5);

        // Process compo stats
        const compoList = compoResponse.data?.results ?? [];
        const entries = entriesResponse.data?.results ?? [];
        compos.value = compoList;
        stats.value.compos = compoList.length;
        stats.value.compoEntries = entries.length;
        recentCompoEntries.value = entries.slice(0, 5);

        // Count entries per compo
        const entryCounts = new Map<number, number>();
        entries.forEach((entry) => {
            entryCounts.set(entry.compo, (entryCounts.get(entry.compo) ?? 0) + 1);
        });
        compoEntryCounts.value = entryCounts;

        // Process competition stats
        const competitionList = competitionsResponse.data?.results ?? [];
        const participants = participantsResponse.data?.results ?? [];
        competitions.value = competitionList;
        stats.value.competitions = competitionList.length;
        stats.value.competitionParticipants = participants.length;

        // Count participants per competition
        const participantCounts = new Map<number, number>();
        participants.forEach((p) => {
            participantCounts.set(p.competition, (participantCounts.get(p.competition) ?? 0) + 1);
        });
        competitionParticipantCounts.value = participantCounts;

        // Process transactions
        const transactions = transactionsResponse.data?.results ?? [];
        const paidTransactions = transactions.filter((t) => t.time_paid).length;
        stats.value.transactions = {
            total: transactions.length,
            paid: paidTransactions,
        };

        // Process vote code requests
        const voteRequests = voteRequestsResponse.data?.results ?? [];
        const pendingRequests = voteRequests.filter((r) => r.status === 0).length;
        stats.value.voteCodeRequests = {
            total: voteRequests.length,
            pending: pendingRequests,
        };
    } catch (e) {
        console.error("Failed to load dashboard data:", e);
    } finally {
        loading.value = false;
    }
}

onMounted(loadDashboardData);
watch(() => props.eventId, loadDashboardData);
</script>
