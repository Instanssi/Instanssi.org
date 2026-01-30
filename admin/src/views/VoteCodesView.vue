<template>
    <LayoutBase :key="`vote-codes-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-data-table-server
                    v-model:items-per-page="perPage"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="headers"
                    :items="voteCodes"
                    :items-length="totalItems"
                    :loading="loading"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('VoteCodesView.noVoteCodesFound')"
                    :loading-text="t('VoteCodesView.loadingVoteCodes')"
                    @update:options="debouncedLoad"
                >
                    <template #item.time="{ item }">
                        {{ item.time ? d(item.time, "long") : "-" }}
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
import { type Ref, computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { TicketVoteCode } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/LayoutBase.vue";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{ eventId: string }>();
const { t, d } = useI18n();
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
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const voteCodes: Ref<TicketVoteCode[]> = ref([]);
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
    try {
        const response = await api.adminEventKompomaattiTicketVoteCodesList({
            path: { event_pk: parseInt(props.eventId, 10) },
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
</script>
