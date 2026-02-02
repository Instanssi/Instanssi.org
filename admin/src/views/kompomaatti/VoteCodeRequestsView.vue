<template>
    <LayoutBase :key="`vote-code-requests-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-text-field
                    v-model="tableState.search.value"
                    variant="outlined"
                    density="compact"
                    :label="t('General.search')"
                    style="max-width: 400px"
                    class="ma-0 pa-0"
                    clearable
                />
            </v-row>
        </v-col>
        <v-col>
            <v-row>
                <v-data-table-server
                    v-model:items-per-page="tableState.perPage.value"
                    :sort-by="tableState.sortByArray.value"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="headers"
                    :items="requests"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="tableState.search.value"
                    :page="tableState.page.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('VoteCodeRequestsView.noRequestsFound')"
                    :loading-text="t('VoteCodeRequestsView.loadingRequests')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.user="{ item }">
                        {{ item.user }}
                    </template>
                    <template #item.status="{ item }">
                        <v-chip :color="getStatusColor(item.status ?? 0)" size="small">
                            {{ getStatusText(item.status ?? 0) }}
                        </v-chip>
                    </template>
                    <template #item.actions="{ item }">
                        <v-btn
                            v-if="
                                (item.status ?? 0) !== 1 &&
                                auth.canChange(PermissionTarget.VOTE_CODE_REQUEST)
                            "
                            color="success"
                            size="small"
                            variant="text"
                            :loading="updatingId === item.id"
                            @click="updateStatus(item.id, 1)"
                        >
                            <FontAwesomeIcon :icon="faCheck" />
                        </v-btn>
                        <v-btn
                            v-if="
                                (item.status ?? 0) !== 2 &&
                                auth.canChange(PermissionTarget.VOTE_CODE_REQUEST)
                            "
                            color="error"
                            size="small"
                            variant="text"
                            :loading="updatingId === item.id"
                            @click="updateStatus(item.id, 2)"
                        >
                            <FontAwesomeIcon :icon="faTimes" />
                        </v-btn>
                        <v-btn
                            v-if="auth.canDelete(PermissionTarget.VOTE_CODE_REQUEST)"
                            color="error"
                            size="small"
                            variant="text"
                            @click="deleteRequest(item)"
                        >
                            <FontAwesomeIcon :icon="faTrash" />
                        </v-btn>
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
        <ConfirmDialog ref="confirmDialog" />
    </LayoutBase>
</template>

<script setup lang="ts">
import { faCheck, faTimes, faTrash } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { StatusEnum, VoteCodeRequest } from "@/api";
import ConfirmDialog from "@/components/dialogs/ConfirmDialog.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { useTableState } from "@/composables/useTableState";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { getApiErrorMessage } from "@/utils/http";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{ eventId: string }>();
const { t } = useI18n();
const toast = useToast();
const auth = useAuth();
const { getEventById } = useEvents();
const eventId = computed(() => parseInt(props.eventId, 10));
const loading = ref(false);
const updatingId = ref<number | null>(null);
const confirmDialog: Ref<InstanceType<typeof ConfirmDialog> | undefined> = ref(undefined);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: getEventById(eventId.value)?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    { title: t("VoteCodeRequestsView.title"), disabled: true },
]);

const tableState = useTableState();
const totalItems = ref(0);
const requests: Ref<VoteCodeRequest[]> = ref([]);
const lastLoadArgs = ref<LoadArgs | null>(null);

const headers: ReadonlyHeaders = [
    {
        title: t("VoteCodeRequestsView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("VoteCodeRequestsView.headers.user"),
        sortable: false,
        key: "user",
    },
    {
        title: t("VoteCodeRequestsView.headers.text"),
        sortable: false,
        key: "text",
    },
    {
        title: t("VoteCodeRequestsView.headers.status"),
        sortable: true,
        key: "status",
    },
    {
        title: t("VoteCodeRequestsView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

function getStatusColor(status: number): string {
    switch (status) {
        case 0:
            return "warning";
        case 1:
            return "success";
        case 2:
            return "error";
        default:
            return "grey";
    }
}

function getStatusText(status: number): string {
    switch (status) {
        case 0:
            return t("VoteCodeRequestsView.statuses.pending");
        case 1:
            return t("VoteCodeRequestsView.statuses.approved");
        case 2:
            return t("VoteCodeRequestsView.statuses.rejected");
        default:
            return "Unknown";
    }
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventKompomaattiVoteCodeRequestsList({
            path: { event_pk: parseInt(props.eventId, 10) },
            query: {
                ...getLoadArgs(args),
            },
        });
        requests.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("VoteCodeRequestsView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

async function updateStatus(id: number, status: StatusEnum) {
    updatingId.value = id;
    try {
        await api.adminEventKompomaattiVoteCodeRequestsPartialUpdate({
            path: { event_pk: parseInt(props.eventId, 10), id },
            body: { status },
        });
        if (lastLoadArgs.value) {
            await load(lastLoadArgs.value);
        }
    } catch (e) {
        toast.error(t("VoteCodeRequestsView.updateFailure"));
        console.error(e);
    } finally {
        updatingId.value = null;
    }
}

async function deleteRequest(item: VoteCodeRequest) {
    await confirmDialog.value?.ifConfirmed(t("VoteCodeRequestsView.confirmDelete"), async () => {
        try {
            await api.adminEventKompomaattiVoteCodeRequestsDestroy({
                path: { event_pk: parseInt(props.eventId, 10), id: item.id },
            });
            toast.success(t("VoteCodeRequestsView.deleteSuccess"));
            if (lastLoadArgs.value) {
                await load(lastLoadArgs.value);
            }
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("VoteCodeRequestsView.deleteFailure")));
            console.error(e);
        }
    });
}

const debouncedLoad = debounce(load, 250);

function onTableOptionsUpdate(args: LoadArgs) {
    tableState.onOptionsUpdate(args);
    debouncedLoad(args);
}

function refresh() {
    tableState.search.value = "";
    tableState.page.value = 1;
    debouncedLoad({
        page: 1,
        itemsPerPage: tableState.perPage.value ?? 25,
        sortBy: [],
        groupBy: [] as never,
        search: "",
    });
}

// Reload when event changes
watch(eventId, refresh);
</script>
