<template>
    <LayoutBase :key="`vote-codes-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-data-table-server
                    v-model:items-per-page="tableState.perPage.value"
                    :sort-by="tableState.sortByArray.value"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="headers"
                    :items="voteCodes"
                    :items-length="totalItems"
                    :loading="loading"
                    :page="tableState.page.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('VoteCodesView.noVoteCodesFound')"
                    :loading-text="t('VoteCodesView.loadingVoteCodes')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.time="{ item }">
                        <DateTimeCell :value="item.time" />
                    </template>
                    <template #item.associated_username="{ item }">
                        {{ item.associated_username ?? "-" }}
                    </template>
                    <template #item.ticket="{ item }">
                        {{ item.ticket ?? "-" }}
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { TicketVoteCode } from "@/api";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { useTableState } from "@/composables/useTableState";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{ eventId: string }>();
const { t } = useI18n();
const toast = useToast();
const { getEventById } = useEvents();
const eventId = computed(() => parseInt(props.eventId, 10));
const loading = ref(false);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: getEventById(eventId.value)?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    { title: t("VoteCodesView.title"), disabled: true },
]);

const tableState = useTableState({ defaultSort: { key: "id", order: "desc" } });
const totalItems = ref(0);
const voteCodes: Ref<TicketVoteCode[]> = ref([]);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);
const headers: ReadonlyHeaders = [
    {
        title: t("VoteCodesView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("VoteCodesView.headers.associatedTo"),
        sortable: false,
        key: "associated_username",
    },
    {
        title: t("VoteCodesView.headers.ticket"),
        sortable: false,
        key: "ticket",
    },
    {
        title: t("VoteCodesView.headers.time"),
        sortable: true,
        key: "time",
    },
];

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventKompomaattiTicketVoteCodesList({
            path: { event_pk: eventId.value },
            query: {
                ...getLoadArgs(args),
            },
        });
        voteCodes.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("VoteCodesView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

function onTableOptionsUpdate(args: LoadArgs) {
    tableState.onOptionsUpdate(args);
    debouncedLoad(args);
}

function refresh() {
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
