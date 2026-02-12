<template>
    <LayoutBase :key="`store-items-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.STORE_ITEM)"
                    color="primary"
                    @click="createItem"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("StoreItemsView.newItem") }}
                </v-btn>
                <v-text-field
                    v-model="tableState.search.value"
                    variant="outlined"
                    density="compact"
                    :label="t('General.search')"
                    style="max-width: 400px"
                    class="ma-0 pa-0 ml-4"
                    clearable
                />
                <v-select
                    v-model="filterAvailable"
                    :items="[
                        { title: t('StoreItemsView.allAvailability'), value: null },
                        { title: t('StoreItemsView.inStockOnly'), value: true },
                        { title: t('StoreItemsView.outOfStockOnly'), value: false },
                    ]"
                    variant="outlined"
                    density="compact"
                    :label="t('StoreItemsView.filterByAvailability')"
                    style="max-width: 180px"
                    class="ma-0 pa-0 ml-4"
                />
                <v-select
                    v-model="filterIsTicket"
                    :items="[
                        { title: t('StoreItemsView.allTypes'), value: null },
                        { title: t('StoreItemsView.ticketsOnly'), value: true },
                        { title: t('StoreItemsView.nonTicketsOnly'), value: false },
                    ]"
                    variant="outlined"
                    density="compact"
                    :label="t('StoreItemsView.filterByType')"
                    style="max-width: 180px"
                    class="ma-0 pa-0 ml-4"
                />
                <v-select
                    v-model="filterIsSecret"
                    :items="[
                        { title: t('StoreItemsView.allVisibility'), value: null },
                        { title: t('StoreItemsView.secretOnly'), value: true },
                        { title: t('StoreItemsView.publicOnly'), value: false },
                    ]"
                    variant="outlined"
                    density="compact"
                    :label="t('StoreItemsView.filterByVisibility')"
                    style="max-width: 180px"
                    class="ma-0 pa-0 ml-4"
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
                    :items="items"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="tableState.search.value"
                    :page="tableState.page.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('StoreItemsView.noItemsFound')"
                    :loading-text="t('StoreItemsView.loadingItems')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.imagefile_thumbnail_url="{ item }">
                        <ImageCell :url="item.imagefile_thumbnail_url" />
                    </template>
                    <template #item.price="{ item }">
                        <PriceCell :value="item.price" />
                    </template>
                    <template #item.available="{ item }">
                        <BooleanIcon :value="item.available" />
                    </template>
                    <template #item.is_ticket="{ item }">
                        <BooleanIcon :value="item.is_ticket" />
                    </template>
                    <template #item.description="{ item }">
                        <LongTextCell :value="item.description" :sanitized-html="true" />
                    </template>
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.STORE_ITEM)"
                            :can-delete="auth.canDelete(PermissionTarget.STORE_ITEM)"
                            :audit-log="{
                                appLabel: 'store',
                                model: 'storeitem',
                                objectPk: item.id,
                            }"
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
import { useRoute, useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import * as api from "@/api";
import type { StoreItem } from "@/api";
import BooleanIcon from "@/components/table/BooleanIcon.vue";
import ImageCell from "@/components/table/ImageCell.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import LongTextCell from "@/components/table/LongTextCell.vue";
import PriceCell from "@/components/table/PriceCell.vue";
import TableActionButtons from "@/components/table/TableActionButtons.vue";
import { useResponsiveHeaders } from "@/composables/useResponsiveHeaders";
import { useTableState } from "@/composables/useTableState";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";
import { getApiErrorMessage } from "@/utils/http";

const props = defineProps<{ eventId: string }>();
const { t } = useI18n();
const route = useRoute();
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
    { title: t("StoreItemsView.title"), disabled: true },
]);

const tableState = useTableState({
    filterKeys: ["available", "is_ticket", "is_secret"],
    initialSort: { key: "id", order: "desc" },
});
const totalItems = ref(0);
const items: Ref<StoreItem[]> = ref([]);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const filterAvailable = tableState.useBooleanFilter("available");
const filterIsTicket = tableState.useBooleanFilter("is_ticket");
const filterIsSecret = tableState.useBooleanFilter("is_secret");

const headers = useResponsiveHeaders(() => [
    {
        title: t("General.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("General.image"),
        sortable: false,
        key: "imagefile_thumbnail_url",
        width: 60,
    },
    {
        title: t("General.name"),
        sortable: true,
        key: "name",
    },
    {
        title: t("General.price"),
        sortable: true,
        key: "price",
    },
    {
        title: t("StoreItemsView.headers.max"),
        sortable: true,
        key: "max",
        minBreakpoint: "lg",
    },
    {
        title: t("StoreItemsView.headers.isAvailable"),
        sortable: false,
        key: "available",
    },
    {
        title: t("StoreItemsView.headers.isTicket"),
        sortable: false,
        key: "is_ticket",
        minBreakpoint: "md",
    },
    {
        title: t("General.description"),
        sortable: false,
        key: "description",
        minBreakpoint: "lg",
    },
    {
        title: t("General.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
]);

function flushData() {
    if (lastLoadArgs.value) {
        load(lastLoadArgs.value);
    }
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventStoreItemsList({
            path: { event_pk: eventId.value },
            query: {
                ...getLoadArgs(args),
                ...(filterAvailable.value !== null ? { available: filterAvailable.value } : {}),
                ...(filterIsTicket.value !== null ? { is_ticket: filterIsTicket.value } : {}),
                ...(filterIsSecret.value !== null ? { is_secret: filterIsSecret.value } : {}),
            },
        });
        items.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("StoreItemsView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

// Reload when filters change
watch([filterAvailable, filterIsTicket, filterIsSecret], () => {
    if (lastLoadArgs.value) {
        debouncedLoad({ ...lastLoadArgs.value, page: 1 });
    }
});

function onTableOptionsUpdate(args: LoadArgs) {
    tableState.onOptionsUpdate(args);
    debouncedLoad(args);
}

function refresh() {
    tableState.setFilter("available", null);
    tableState.setFilter("is_ticket", null);
    tableState.setFilter("is_secret", null);
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

async function deleteItem(item: StoreItem): Promise<void> {
    const text = t("StoreItemsView.confirmDelete", item);
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventStoreItemsDestroy({
                path: { event_pk: eventId.value, id: item.id },
            });
            toast.success(t("StoreItemsView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("StoreItemsView.deleteFailure")));
            console.error(e);
        }
    });
}

function editItem(id: number): void {
    router.push({
        name: "store-items-edit",
        params: { eventId: eventId.value, id },
        query: route.query,
    });
}

function createItem(): void {
    router.push({
        name: "store-items-new",
        params: { eventId: eventId.value },
        query: route.query,
    });
}
</script>
