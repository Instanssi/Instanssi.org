<template>
    <LayoutBase :key="`store-items-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn v-if="auth.canAdd(PermissionTarget.STORE_ITEM)" @click="createItem">
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("StoreItemsView.newItem") }}
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
            </v-row>
        </v-col>
        <v-col>
            <v-row>
                <v-data-table-server
                    :key="`store-items-table-${refreshKey}`"
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
                    :no-data-text="t('StoreItemsView.noItemsFound')"
                    :loading-text="t('StoreItemsView.loadingItems')"
                    @update:options="debouncedLoad"
                >
                    <template #item.price="{ item }">
                        <PriceCell :value="item.price" />
                    </template>
                    <template #item.num_available="{ item }">
                        {{ item.num_available }}
                    </template>
                    <template #item.available="{ item }">
                        <BooleanIcon :value="item.available" />
                    </template>
                    <template #item.is_ticket="{ item }">
                        <BooleanIcon :value="item.is_ticket" />
                    </template>
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.STORE_ITEM)"
                            :can-delete="auth.canDelete(PermissionTarget.STORE_ITEM)"
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
import { type Ref, computed, inject, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { StoreItem } from "@/api";
import BooleanIcon from "@/components/table/BooleanIcon.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import PriceCell from "@/components/table/PriceCell.vue";
import TableActionButtons from "@/components/table/TableActionButtons.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";

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
    { title: t("StoreItemsView.title"), disabled: true },
]);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const items: Ref<StoreItem[]> = ref([]);
const search = ref("");
const refreshKey = ref(0);

const headers: ReadonlyHeaders = [
    {
        title: t("StoreItemsView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("StoreItemsView.headers.name"),
        sortable: true,
        key: "name",
    },
    {
        title: t("StoreItemsView.headers.price"),
        sortable: true,
        key: "price",
    },
    {
        title: t("StoreItemsView.headers.available"),
        sortable: false,
        key: "num_available",
    },
    {
        title: t("StoreItemsView.headers.max"),
        sortable: true,
        key: "max",
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
    },
    {
        title: t("StoreItemsView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

function flushData() {
    refreshKey.value += 1;
}

async function load(args: LoadArgs) {
    loading.value = true;
    try {
        const response = await api.adminEventStoreItemsList({
            path: { event_pk: eventId.value },
            query: getLoadArgs(args),
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
            toast.error(t("StoreItemsView.deleteFailure"));
            console.error(e);
        }
    });
}

function editItem(id: number): void {
    router.push({ name: "store-items-edit", params: { eventId: eventId.value, id } });
}

function createItem(): void {
    router.push({ name: "store-items-new", params: { eventId: eventId.value } });
}
</script>
