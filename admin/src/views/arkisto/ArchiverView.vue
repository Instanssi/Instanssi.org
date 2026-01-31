<template>
    <LayoutBase :key="`archiver-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <!-- Warning when event is ongoing -->
            <v-row v-if="status?.ongoing_activity" class="mb-4">
                <v-col cols="12">
                    <v-alert type="warning" variant="tonal" prominent>
                        <template #prepend>
                            <FontAwesomeIcon :icon="faExclamationTriangle" size="lg" />
                        </template>
                        {{ t("ArchiverView.ongoingWarning") }}
                    </v-alert>
                </v-col>
            </v-row>

            <!-- Archive Visibility -->
            <v-row class="mb-4">
                <v-col cols="12">
                    <v-card>
                        <v-card-title class="d-flex align-center">
                            <FontAwesomeIcon :icon="faEye" class="mr-2" />
                            {{ t("ArchiverView.visibility.title") }}
                        </v-card-title>
                        <v-card-text>
                            <p class="mb-4">{{ t("ArchiverView.visibility.description") }}</p>
                            <v-chip :color="status?.is_archived ? 'success' : 'grey'" class="mb-4">
                                <FontAwesomeIcon
                                    :icon="status?.is_archived ? faCheck : faTimes"
                                    class="mr-2"
                                />
                                {{
                                    status?.is_archived
                                        ? t("ArchiverView.visibility.visible")
                                        : t("ArchiverView.visibility.hidden")
                                }}
                            </v-chip>
                        </v-card-text>
                        <v-card-actions>
                            <v-btn
                                v-if="status?.is_archived"
                                color="warning"
                                :loading="actionLoading === 'hide'"
                                :disabled="!!actionLoading"
                                @click="hideFromArchive"
                            >
                                <template #prepend>
                                    <FontAwesomeIcon :icon="faEyeSlash" />
                                </template>
                                {{ t("ArchiverView.visibility.hideBtn") }}
                            </v-btn>
                            <v-btn
                                v-else
                                color="success"
                                :loading="actionLoading === 'show'"
                                :disabled="!!actionLoading"
                                @click="showInArchive"
                            >
                                <template #prepend>
                                    <FontAwesomeIcon :icon="faEye" />
                                </template>
                                {{ t("ArchiverView.visibility.showBtn") }}
                            </v-btn>
                        </v-card-actions>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Voting Data -->
            <v-row class="mb-4">
                <v-col cols="12">
                    <v-card>
                        <v-card-title class="d-flex align-center">
                            <FontAwesomeIcon :icon="faChartBar" class="mr-2" />
                            {{ t("ArchiverView.votingData.title") }}
                        </v-card-title>
                        <v-card-text>
                            <p class="mb-4">{{ t("ArchiverView.votingData.description") }}</p>

                            <!-- Scores Status -->
                            <div class="mb-4">
                                <strong>{{ t("ArchiverView.votingData.scoresStatus") }}</strong>
                                <v-chip
                                    :color="status?.votes_unoptimized ? 'warning' : 'success'"
                                    class="ml-2"
                                >
                                    <FontAwesomeIcon
                                        :icon="status?.votes_unoptimized ? faTimes : faCheck"
                                        class="mr-2"
                                    />
                                    {{
                                        status?.votes_unoptimized
                                            ? t("ArchiverView.votingData.notOptimized")
                                            : t("ArchiverView.votingData.optimized")
                                    }}
                                </v-chip>
                            </div>

                            <!-- Old Votes Status -->
                            <div>
                                <strong>{{ t("ArchiverView.votingData.oldVotesStatus") }}</strong>
                                <v-chip
                                    :color="status?.old_votes_found ? 'info' : 'success'"
                                    class="ml-2"
                                >
                                    <FontAwesomeIcon
                                        :icon="status?.old_votes_found ? faDatabase : faCheck"
                                        class="mr-2"
                                    />
                                    {{
                                        status?.old_votes_found
                                            ? t("ArchiverView.votingData.oldVotesFound")
                                            : t("ArchiverView.votingData.noOldVotes")
                                    }}
                                </v-chip>
                            </div>
                        </v-card-text>
                        <v-card-actions>
                            <v-btn
                                color="primary"
                                :loading="actionLoading === 'optimize'"
                                :disabled="
                                    !!actionLoading ||
                                    status?.ongoing_activity ||
                                    !status?.votes_unoptimized
                                "
                                @click="optimizeScores"
                            >
                                <template #prepend>
                                    <FontAwesomeIcon :icon="faChartBar" />
                                </template>
                                {{ t("ArchiverView.votingData.optimizeBtn") }}
                            </v-btn>
                            <v-btn
                                color="error"
                                :loading="actionLoading === 'removeVotes'"
                                :disabled="
                                    !!actionLoading ||
                                    status?.ongoing_activity ||
                                    status?.votes_unoptimized ||
                                    !status?.old_votes_found
                                "
                                @click="confirmRemoveVotes"
                            >
                                <template #prepend>
                                    <FontAwesomeIcon :icon="faTrash" />
                                </template>
                                {{ t("ArchiverView.votingData.removeVotesBtn") }}
                            </v-btn>
                        </v-card-actions>
                    </v-card>
                </v-col>
            </v-row>

            <!-- User Rights Transfer -->
            <v-row class="mb-4">
                <v-col cols="12">
                    <v-card>
                        <v-card-title class="d-flex align-center">
                            <FontAwesomeIcon :icon="faUserShield" class="mr-2" />
                            {{ t("ArchiverView.userRights.title") }}
                        </v-card-title>
                        <v-card-text>
                            <p class="mb-4">{{ t("ArchiverView.userRights.description") }}</p>
                            <v-chip
                                :color="status?.has_non_archived_items ? 'warning' : 'success'"
                                class="mb-4"
                            >
                                <FontAwesomeIcon
                                    :icon="status?.has_non_archived_items ? faUsers : faCheck"
                                    class="mr-2"
                                />
                                {{
                                    status?.has_non_archived_items
                                        ? t("ArchiverView.userRights.hasNonArchived")
                                        : t("ArchiverView.userRights.allTransferred")
                                }}
                            </v-chip>
                        </v-card-text>
                        <v-card-actions>
                            <v-btn
                                color="error"
                                :loading="actionLoading === 'transfer'"
                                :disabled="
                                    !!actionLoading ||
                                    status?.ongoing_activity ||
                                    !status?.has_non_archived_items
                                "
                                @click="confirmTransferRights"
                            >
                                <template #prepend>
                                    <FontAwesomeIcon :icon="faUserShield" />
                                </template>
                                {{ t("ArchiverView.userRights.transferBtn") }}
                            </v-btn>
                        </v-card-actions>
                    </v-card>
                </v-col>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import {
    faChartBar,
    faCheck,
    faDatabase,
    faExclamationTriangle,
    faEye,
    faEyeSlash,
    faTimes,
    faTrash,
    faUserShield,
    faUsers,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { parseInt } from "lodash-es";
import { computed, inject, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";

import * as api from "@/api";
import type { ArchiverStatus } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { useEvents } from "@/services/events";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";

const props = defineProps<{ eventId: string }>();
const { t } = useI18n();
const toast = useToast();
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;
const { getEventById } = useEvents();
const eventId = computed(() => parseInt(props.eventId, 10));
const loading = ref(false);
const actionLoading = ref<string | null>(null);
const status = ref<ArchiverStatus | null>(null);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: getEventById(eventId.value)?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    { title: t("ArchiverView.title"), disabled: true },
]);

async function loadStatus() {
    loading.value = true;
    try {
        const response = await api.adminEventArkistoArchiverStatusRetrieve({
            path: { event_pk: eventId.value },
        });
        status.value = response.data!;
    } catch (e) {
        toast.error(t("ArchiverView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

async function showInArchive() {
    actionLoading.value = "show";
    try {
        const response = await api.adminEventArkistoArchiverShowCreate({
            path: { event_pk: eventId.value },
        });
        status.value = response.data!;
        toast.success(t("ArchiverView.visibility.showSuccess"));
    } catch (e) {
        toast.error(t("ArchiverView.visibility.showFailure"));
        console.error(e);
    } finally {
        actionLoading.value = null;
    }
}

async function hideFromArchive() {
    actionLoading.value = "hide";
    try {
        const response = await api.adminEventArkistoArchiverHideCreate({
            path: { event_pk: eventId.value },
        });
        status.value = response.data!;
        toast.success(t("ArchiverView.visibility.hideSuccess"));
    } catch (e) {
        toast.error(t("ArchiverView.visibility.hideFailure"));
        console.error(e);
    } finally {
        actionLoading.value = null;
    }
}

async function optimizeScores() {
    actionLoading.value = "optimize";
    try {
        const response = await api.adminEventArkistoArchiverOptimizeScoresCreate({
            path: { event_pk: eventId.value },
        });
        status.value = response.data!;
        toast.success(t("ArchiverView.votingData.optimizeSuccess"));
    } catch (e) {
        toast.error(t("ArchiverView.votingData.optimizeFailure"));
        console.error(e);
    } finally {
        actionLoading.value = null;
    }
}

async function confirmRemoveVotes() {
    const text = t("ArchiverView.votingData.removeVotesConfirm");
    await confirmDialog.value!.ifConfirmed(text, async () => {
        actionLoading.value = "removeVotes";
        try {
            const response = await api.adminEventArkistoArchiverRemoveOldVotesCreate({
                path: { event_pk: eventId.value },
            });
            status.value = response.data!;
            toast.success(t("ArchiverView.votingData.removeVotesSuccess"));
        } catch (e) {
            toast.error(t("ArchiverView.votingData.removeVotesFailure"));
            console.error(e);
        } finally {
            actionLoading.value = null;
        }
    });
}

async function confirmTransferRights() {
    const text = t("ArchiverView.userRights.transferConfirm");
    await confirmDialog.value!.ifConfirmed(text, async () => {
        actionLoading.value = "transfer";
        try {
            const response = await api.adminEventArkistoArchiverTransferRightsCreate({
                path: { event_pk: eventId.value },
            });
            status.value = response.data!;
            toast.success(t("ArchiverView.userRights.transferSuccess"));
        } catch (e) {
            toast.error(t("ArchiverView.userRights.transferFailure"));
            console.error(e);
        } finally {
            actionLoading.value = null;
        }
    });
}

onMounted(loadStatus);
</script>
