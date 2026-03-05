<template>
    <LayoutBase :key="`live-voting-${eventId}-${compoId}`" :breadcrumbs="breadcrumbs">
        <v-col v-if="!state">
            <v-progress-circular v-if="loading" indeterminate size="64" />
            <v-alert v-else type="error">{{ t("LiveVotingView.loadFailure") }}</v-alert>
        </v-col>
        <v-col v-else>
            <v-row class="mt-2" align="center">
                <v-col cols="auto">
                    <FontAwesomeIcon :icon="faClock" class="mr-1" />
                    {{ t("LiveVotingView.votingEnd") }}
                    <DateTimeCell :value="votingEnd" format="short" />
                    <v-chip v-if="votingEnded" color="error" size="small" class="ml-2">
                        {{ t("LiveVotingView.votingTimeEnded") }}
                    </v-chip>
                </v-col>
            </v-row>

            <v-row class="mt-2">
                <v-col cols="auto">
                    <v-btn
                        :color="state.voting_open ? 'warning' : 'success'"
                        :loading="actionLoading"
                        :disabled="!state.voting_open && votingEnded"
                        @click="toggleVoting"
                    >
                        <FontAwesomeIcon
                            :icon="state.voting_open ? faLock : faLockOpen"
                            class="mr-2"
                        />
                        {{
                            state.voting_open
                                ? t("LiveVotingView.closeVoting")
                                : t("LiveVotingView.openVoting")
                        }}
                    </v-btn>
                </v-col>
                <v-col cols="auto">
                    <v-btn-group divided color="primary" density="compact">
                        <v-btn :loading="actionLoading" @click="revealAll">
                            <FontAwesomeIcon :icon="faEye" class="mr-2" />
                            {{ t("LiveVotingView.revealAll") }}
                        </v-btn>
                        <v-btn :loading="actionLoading" @click="hideAll">
                            <FontAwesomeIcon :icon="faEyeSlash" class="mr-2" />
                            {{ t("LiveVotingView.hideAll") }}
                        </v-btn>
                    </v-btn-group>
                </v-col>
                <v-col cols="auto">
                    <v-btn color="error" :loading="actionLoading" @click="confirmReset">
                        <FontAwesomeIcon :icon="faRotateLeft" class="mr-2" />
                        {{ t("LiveVotingView.reset") }}
                    </v-btn>
                </v-col>
            </v-row>

            <v-row class="mt-2">
                <v-col cols="12">
                    <v-list lines="two" density="compact">
                        <v-list-item
                            v-for="entry in state.entries"
                            :key="entry.id"
                            :class="{
                                'bg-light-blue-lighten-5': state.current_entry === entry.id,
                            }"
                        >
                            <template #prepend>
                                <v-avatar
                                    v-if="entry.imagefile_thumbnail_url"
                                    :image="entry.imagefile_thumbnail_url"
                                    rounded="sm"
                                    size="48"
                                    class="mr-3"
                                />
                                <v-avatar
                                    v-else
                                    color="grey-lighten-2"
                                    rounded="sm"
                                    size="48"
                                    class="mr-3"
                                >
                                    <FontAwesomeIcon :icon="faFileAudio" />
                                </v-avatar>
                            </template>

                            <v-list-item-title class="font-weight-medium">
                                {{ entry.name }}
                            </v-list-item-title>
                            <v-list-item-subtitle>
                                {{ entry.creator }}
                            </v-list-item-subtitle>

                            <template #append>
                                <v-chip
                                    v-if="state.current_entry === entry.id"
                                    color="primary"
                                    size="small"
                                    class="mr-2"
                                >
                                    {{ t("LiveVotingView.onScreen") }}
                                </v-chip>
                                <v-btn
                                    v-if="!entry.live_voting_revealed"
                                    color="primary"
                                    size="small"
                                    variant="elevated"
                                    :disabled="!state.voting_open"
                                    :loading="actionLoading"
                                    @click="revealEntry(entry.id)"
                                >
                                    <FontAwesomeIcon :icon="faEye" class="mr-1" />
                                    {{ t("LiveVotingView.reveal") }}
                                </v-btn>
                                <template v-else>
                                    <v-chip color="success" size="small" class="mr-2">
                                        {{ t("LiveVotingView.revealed") }}
                                    </v-chip>
                                    <v-btn
                                        size="small"
                                        variant="text"
                                        :loading="actionLoading"
                                        @click="hideEntry(entry.id)"
                                    >
                                        <FontAwesomeIcon :icon="faEyeSlash" class="mr-1" />
                                        {{ t("LiveVotingView.hide") }}
                                    </v-btn>
                                </template>
                            </template>
                        </v-list-item>
                    </v-list>
                </v-col>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import {
    faClock,
    faEye,
    faEyeSlash,
    faFileAudio,
    faLock,
    faLockOpen,
    faRotateLeft,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, inject, onMounted, onUnmounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";

import * as api from "@/api";
import type { LiveVotingState } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
import { useEvents } from "@/services/events";
import { confirmDialogKey, type ConfirmDialogType } from "@/symbols";

const props = defineProps<{ eventId: string; compoId: string }>();
const { t } = useI18n();
const toast = useToast();
const { getEventById } = useEvents();
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;
const eventId = computed(() => parseInt(props.eventId, 10));
const compoId = computed(() => parseInt(props.compoId, 10));

const breadcrumbs = computed((): BreadcrumbItem[] => [
    {
        title: getEventById(eventId.value)?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    {
        title: t("ComposView.title"),
        to: { name: "compos", params: { eventId: props.eventId } },
    },
    {
        title: compoName.value || "...",
        to: { name: "compos-edit", params: { eventId: props.eventId, id: props.compoId } },
    },
    { title: t("LiveVotingView.title"), disabled: true },
]);

const compoName = ref("");
const votingEnd = ref<string | null>(null);
const votingEnded = computed(() => {
    if (!votingEnd.value) return false;
    return new Date(votingEnd.value) < new Date();
});
const state = ref<LiveVotingState | null>(null);
const loading = ref(false);
const actionLoading = ref(false);
let pollTimer: ReturnType<typeof setInterval> | null = null;

async function loadState() {
    try {
        const response = await api.adminEventKompomaattiLiveVotingRetrieve({
            path: { event_pk: eventId.value, id: compoId.value },
        });
        if (response.data) {
            state.value = response.data;
        }
    } catch (e) {
        console.error(e);
    }
}

async function loadCompoName() {
    try {
        const response = await api.adminEventKompomaattiComposRetrieve({
            path: { event_pk: eventId.value, id: compoId.value },
        });
        if (response.data) {
            compoName.value = response.data.name;
            votingEnd.value = response.data.voting_end;
        }
    } catch (e) {
        console.error(e);
    }
}

async function toggleVoting() {
    if (!state.value) return;
    const message = state.value.voting_open
        ? t("LiveVotingView.closeVotingConfirm")
        : t("LiveVotingView.openVotingConfirm");
    const result = await confirmDialog.value!.confirm(message);
    if (!result) return;
    actionLoading.value = true;
    try {
        const response = await api.adminEventKompomaattiLiveVotingPartialUpdate({
            path: { event_pk: eventId.value, id: compoId.value },
            body: { voting_open: !state.value.voting_open },
        });
        if (response.data) {
            state.value = response.data;
        }
    } catch (e) {
        toast.error(t("LiveVotingView.actionFailure"));
        console.error(e);
    } finally {
        actionLoading.value = false;
    }
}

async function revealEntry(entryId: number) {
    actionLoading.value = true;
    try {
        const response = await api.adminEventKompomaattiLiveVotingRevealEntryCreate({
            path: { event_pk: eventId.value, id: compoId.value },
            body: { entry_id: entryId },
        });
        if (response.data) {
            state.value = response.data;
        }
    } catch (e) {
        toast.error(t("LiveVotingView.actionFailure"));
        console.error(e);
    } finally {
        actionLoading.value = false;
    }
}

async function hideEntry(entryId: number) {
    actionLoading.value = true;
    try {
        const response = await api.adminEventKompomaattiLiveVotingHideEntryCreate({
            path: { event_pk: eventId.value, id: compoId.value },
            body: { entry_id: entryId },
        });
        if (response.data) {
            state.value = response.data;
        }
    } catch (e) {
        toast.error(t("LiveVotingView.actionFailure"));
        console.error(e);
    } finally {
        actionLoading.value = false;
    }
}

async function hideAll() {
    const result = await confirmDialog.value!.confirm(t("LiveVotingView.hideAllConfirm"));
    if (!result) return;
    actionLoading.value = true;
    try {
        const response = await api.adminEventKompomaattiLiveVotingHideAllCreate({
            path: { event_pk: eventId.value, id: compoId.value },
        });
        if (response.data) {
            state.value = response.data;
        }
    } catch (e) {
        toast.error(t("LiveVotingView.actionFailure"));
        console.error(e);
    } finally {
        actionLoading.value = false;
    }
}

async function revealAll() {
    const result = await confirmDialog.value!.confirm(t("LiveVotingView.revealAllConfirm"));
    if (!result) return;
    actionLoading.value = true;
    try {
        const response = await api.adminEventKompomaattiLiveVotingRevealAllCreate({
            path: { event_pk: eventId.value, id: compoId.value },
        });
        if (response.data) {
            state.value = response.data;
        }
    } catch (e) {
        toast.error(t("LiveVotingView.actionFailure"));
        console.error(e);
    } finally {
        actionLoading.value = false;
    }
}

async function confirmReset() {
    const result = await confirmDialog.value!.confirm(t("LiveVotingView.resetConfirm"));
    if (!result) return;
    actionLoading.value = true;
    try {
        const response = await api.adminEventKompomaattiLiveVotingResetCreate({
            path: { event_pk: eventId.value, id: compoId.value },
        });
        if (response.data) {
            state.value = response.data;
        }
    } catch (e) {
        toast.error(t("LiveVotingView.actionFailure"));
        console.error(e);
    } finally {
        actionLoading.value = false;
    }
}

function startPolling() {
    stopPolling();
    pollTimer = setInterval(loadState, 3000);
}

function stopPolling() {
    if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
    }
}

onMounted(async () => {
    loading.value = true;
    await Promise.all([loadCompoName(), loadState()]);
    loading.value = false;
    startPolling();
});

onUnmounted(() => {
    stopPolling();
});
</script>
