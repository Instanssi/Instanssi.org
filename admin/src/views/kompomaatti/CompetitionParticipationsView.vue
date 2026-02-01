<template>
    <LayoutBase :key="`participations-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.COMPETITION_PARTICIPATION)"
                    @click="createParticipation"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("CompetitionParticipationsView.newParticipation") }}
                </v-btn>
                <v-select
                    v-model="selectedCompetition"
                    :items="competitionOptions"
                    variant="outlined"
                    density="compact"
                    :label="t('CompetitionParticipationsView.filterByCompetition')"
                    style="max-width: 300px"
                    class="ma-0 pa-0 ml-4"
                    clearable
                />
            </v-row>
        </v-col>
        <v-col>
            <v-row>
                <v-data-table-server
                    v-model:items-per-page="perPage"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="headers"
                    :items="participations"
                    :items-length="totalItems"
                    :loading="loading"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('CompetitionParticipationsView.noParticipationsFound')"
                    :loading-text="t('CompetitionParticipationsView.loadingParticipations')"
                    @update:options="debouncedLoad"
                >
                    <template #item.competition="{ item }">
                        {{ getCompetitionName(item.competition) }}
                    </template>
                    <template #item.user="{ item }">
                        {{ getUserName(item.user) }}
                    </template>
                    <template #item.disqualified="{ item }">
                        <FontAwesomeIcon
                            v-if="item.disqualified"
                            :icon="faCheck"
                            class="text-red"
                        />
                        <FontAwesomeIcon v-else :icon="faXmark" class="text-green" />
                    </template>
                    <template #item.rank="{ item }">
                        {{ item.rank ?? "-" }}
                    </template>
                    <template #item.actions="{ item }">
                        <v-btn
                            v-if="auth.canDelete(PermissionTarget.COMPETITION_PARTICIPATION)"
                            density="compact"
                            variant="text"
                            color="red"
                            @click="deleteParticipation(item)"
                        >
                            <template #prepend>
                                <FontAwesomeIcon :icon="faXmark" />
                            </template>
                            {{ t("General.delete") }}
                        </v-btn>
                        <v-btn
                            v-if="auth.canChange(PermissionTarget.COMPETITION_PARTICIPATION)"
                            density="compact"
                            variant="text"
                            @click="editParticipation(item.id)"
                        >
                            <template #prepend>
                                <FontAwesomeIcon :icon="faPenToSquare" />
                            </template>
                            {{ t("General.edit") }}
                        </v-btn>
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { faCheck, faPenToSquare, faPlus, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, inject, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { Competition, CompetitionParticipation, User } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";
import { getApiErrorMessage } from "@/utils/http";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{ eventId: string }>();
const { t } = useI18n();
const router = useRouter();
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;
const toast = useToast();
const auth = useAuth();
const { getEventById } = useEvents();
const eventId = computed(() => parseInt(props.eventId, 10));
const loading = ref(false);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: getEventById(eventId.value)?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    { title: t("CompetitionParticipationsView.title"), disabled: true },
]);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const participations: Ref<CompetitionParticipation[]> = ref([]);
const competitions: Ref<Competition[]> = ref([]);
const users: Ref<User[]> = ref([]);
const selectedCompetition: Ref<number | null> = ref(null);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const headers: ReadonlyHeaders = [
    {
        title: t("CompetitionParticipationsView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("CompetitionParticipationsView.headers.participantName"),
        sortable: true,
        key: "participant_name",
    },
    {
        title: t("CompetitionParticipationsView.headers.user"),
        sortable: false,
        key: "user",
    },
    {
        title: t("CompetitionParticipationsView.headers.competition"),
        sortable: false,
        key: "competition",
    },
    {
        title: t("CompetitionParticipationsView.headers.score"),
        sortable: true,
        key: "score",
    },
    {
        title: t("CompetitionParticipationsView.headers.disqualified"),
        sortable: false,
        key: "disqualified",
    },
    {
        title: t("CompetitionParticipationsView.headers.rank"),
        sortable: false,
        key: "rank",
    },
    {
        title: t("CompetitionParticipationsView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

const competitionOptions = computed(() => [
    { title: t("CompetitionParticipationsView.allCompetitions"), value: null },
    ...competitions.value.map((c) => ({ title: c.name, value: c.id })),
]);

function getCompetitionName(competitionId: number): string {
    const competition = competitions.value.find((c) => c.id === competitionId);
    return competition?.name ?? `#${competitionId}`;
}

function getUserName(userId: number): string {
    const user = users.value.find((u) => u.id === userId);
    return user?.username ?? `#${userId}`;
}

function flushData() {
    if (lastLoadArgs.value) {
        load(lastLoadArgs.value);
    }
}

async function loadCompetitions() {
    try {
        const response = await api.adminEventKompomaattiCompetitionsList({
            path: { event_pk: eventId.value },
            query: { limit: 100 },
        });
        competitions.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load competitions:", e);
    }
}

async function loadUsers() {
    try {
        const response = await api.adminUsersList({
            query: { limit: 1000 },
        });
        users.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load users:", e);
    }
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventKompomaattiCompetitionParticipationsList({
            path: { event_pk: parseInt(props.eventId, 10) },
            query: {
                ...getLoadArgs(args),
                ...(selectedCompetition.value ? { competition: selectedCompetition.value } : {}),
            },
        });
        participations.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("CompetitionParticipationsView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

// Reload when competition filter changes
watch(selectedCompetition, () => {
    if (lastLoadArgs.value) {
        debouncedLoad(lastLoadArgs.value);
    }
});

function refresh() {
    selectedCompetition.value = null;
    loadCompetitions();
    debouncedLoad({
        page: 1,
        itemsPerPage: perPage.value ?? 25,
        sortBy: [],
        groupBy: [] as never,
        search: "",
    });
}

// Reload competitions when event changes
watch(eventId, refresh);

async function deleteParticipation(item: CompetitionParticipation): Promise<void> {
    const text = t("CompetitionParticipationsView.confirmDelete", {
        name: item.participant_name || `#${item.id}`,
    });
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventKompomaattiCompetitionParticipationsDestroy({
                path: { event_pk: eventId.value, id: item.id },
            });
            toast.success(t("CompetitionParticipationsView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("CompetitionParticipationsView.deleteFailure")));
            console.error(e);
        }
    });
}

function editParticipation(id: number): void {
    router.push({
        name: "competition-participations-edit",
        params: { eventId: eventId.value, id },
    });
}

function createParticipation(): void {
    router.push({ name: "competition-participations-new", params: { eventId: eventId.value } });
}

onMounted(() => {
    loadCompetitions();
    loadUsers();
});
</script>
