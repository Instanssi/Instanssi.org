<template>
    <LayoutBase :key="`program-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn v-if="auth.canAdd(PermissionTarget.PROGRAMME_EVENT)" @click="createItem">
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("ProgramEventsView.newProgramEvent") }}
                </v-btn>
                <v-text-field
                    v-model="search"
                    variant="outlined"
                    density="compact"
                    :label="t('General.search')"
                    style="max-width: 400px"
                    class="ma-0 pa-0 ml-4"
                    clearable
                />
                <v-select
                    v-model="filterEventType"
                    variant="outlined"
                    density="compact"
                    :label="t('ProgramEventsView.filterEventType')"
                    :items="eventTypeFilterOptions"
                    style="max-width: 200px"
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
                    :items="items"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="search"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('ProgramEventsView.noProgramEventsFound')"
                    :loading-text="t('ProgramEventsView.loadingProgramEvents')"
                    @update:options="debouncedLoad"
                >
                    <template #item.icon_small_url="{ item }">
                        <ImageCell :url="item.icon_small_url" />
                    </template>
                    <template #item.icon2_small_url="{ item }">
                        <ImageCell :url="item.icon2_small_url" />
                    </template>
                    <template #item.start="{ item }">
                        <DateTimeCell :value="item.start" />
                    </template>
                    <template #item.end="{ item }">
                        <DateTimeCell :value="item.end" />
                    </template>
                    <template #item.social_links="{ item }">
                        <SocialLinksCell
                            :home-url="item.home_url"
                            :twitter-url="item.twitter_url"
                            :github-url="item.github_url"
                            :facebook-url="item.facebook_url"
                            :linkedin-url="item.linkedin_url"
                            :wiki-url="item.wiki_url"
                        />
                    </template>
                    <template #item.event_type="{ item }">
                        {{ t(`ProgramEventsView.eventTypes.${item.event_type}`) }}
                    </template>
                    <template #item.active="{ item }">
                        <BooleanIcon :value="item.active" />
                    </template>
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.PROGRAMME_EVENT)"
                            :can-delete="auth.canDelete(PermissionTarget.PROGRAMME_EVENT)"
                            @edit="editItem(item.id)"
                            @delete="deleteItem(item)"
                        />
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, inject, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTableServer, VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { ProgramEvent } from "@/api";
import BooleanIcon from "@/components/table/BooleanIcon.vue";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
import ImageCell from "@/components/table/ImageCell.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import SocialLinksCell from "@/components/table/SocialLinksCell.vue";
import TableActionButtons from "@/components/table/TableActionButtons.vue";
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
    { title: t("ProgramEventsView.title"), disabled: true },
]);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const items: Ref<ProgramEvent[]> = ref([]);
const search = ref("");
const filterEventType: Ref<0 | 1 | null> = ref(null);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const eventTypeFilterOptions = [
    { title: t("ProgramEventsView.eventTypes.0"), value: 0 },
    { title: t("ProgramEventsView.eventTypes.1"), value: 1 },
];

const headers: ReadonlyHeaders = [
    {
        title: t("ProgramEventsView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("ProgramEventsView.headers.icon"),
        sortable: false,
        key: "icon_small_url",
        width: 60,
    },
    {
        title: t("ProgramEventsView.headers.icon2"),
        sortable: false,
        key: "icon2_small_url",
        width: 60,
    },
    {
        title: t("ProgramEventsView.headers.title"),
        sortable: false,
        key: "title",
    },
    {
        title: t("ProgramEventsView.headers.start"),
        sortable: true,
        key: "start",
    },
    {
        title: t("ProgramEventsView.headers.end"),
        sortable: true,
        key: "end",
    },
    {
        title: t("ProgramEventsView.headers.place"),
        sortable: false,
        key: "place",
    },
    {
        title: t("ProgramEventsView.headers.socialLinks"),
        sortable: false,
        key: "social_links",
    },
    {
        title: t("ProgramEventsView.headers.eventType"),
        sortable: false,
        key: "event_type",
    },
    {
        title: t("ProgramEventsView.headers.active"),
        sortable: false,
        key: "active",
    },
    {
        title: t("ProgramEventsView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

function flushData() {
    if (lastLoadArgs.value) {
        load(lastLoadArgs.value);
    }
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventProgramEventsList({
            path: { event_pk: eventId.value },
            query: {
                ...getLoadArgs(args),
                ...(filterEventType.value !== null ? { event_type: filterEventType.value } : {}),
            },
        });
        items.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("ProgramEventsView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

// Watch filter and reload when it changes
watch(filterEventType, () => {
    flushData();
});

function refresh() {
    filterEventType.value = null;
    search.value = "";
    debouncedLoad({
        page: 1,
        itemsPerPage: perPage.value ?? 25,
        sortBy: [],
        groupBy: [] as never,
        search: "",
    });
}

// Reload when event changes
watch(eventId, refresh);

async function deleteItem(item: ProgramEvent): Promise<void> {
    const text = t("ProgramEventsView.confirmDelete", item);
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventProgramEventsDestroy({
                path: { event_pk: eventId.value, id: item.id },
            });
            toast.success(t("ProgramEventsView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("ProgramEventsView.deleteFailure")));
            console.error(e);
        }
    });
}

function editItem(id: number): void {
    router.push({ name: "program-edit", params: { eventId: eventId.value, id } });
}

function createItem(): void {
    router.push({ name: "program-new", params: { eventId: eventId.value } });
}
</script>
