<template>
    <LayoutBase :key="`infodesk-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-text-field
                    v-model="tableState.search.value"
                    variant="outlined"
                    density="compact"
                    :label="t('InfodeskView.searchPlaceholder')"
                    style="max-width: 500px"
                    class="ma-0 pa-0"
                    clearable
                    autofocus
                />
            </v-row>
        </v-col>

        <!-- Transaction Items Table -->
        <v-col>
            <v-row>
                <v-data-table-server
                    v-model:items-per-page="tableState.perPage.value"
                    :sort-by="tableState.sortByArray.value"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="itemHeaders"
                    :items="items"
                    :items-length="totalItems"
                    :loading="itemsLoading"
                    :search="tableState.search.value"
                    :page="tableState.page.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('InfodeskView.noItemsFound')"
                    :loading-text="t('InfodeskView.loading')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.transaction_is_paid="{ item }">
                        <v-chip
                            :color="item.transaction_is_paid ? 'success' : 'error'"
                            size="small"
                            variant="flat"
                        >
                            {{
                                item.transaction_is_paid
                                    ? t("InfodeskView.paid")
                                    : t("InfodeskView.notPaid")
                            }}
                        </v-chip>
                    </template>
                    <template #item.is_delivered="{ item }">
                        <v-chip
                            :color="item.is_delivered ? 'success' : 'warning'"
                            size="small"
                            variant="flat"
                        >
                            {{
                                item.is_delivered
                                    ? t("InfodeskView.delivered")
                                    : t("InfodeskView.notDelivered")
                            }}
                        </v-chip>
                    </template>
                    <template #item.actions="{ item }">
                        <v-btn size="small" variant="text" @click="viewItem(item.id)">
                            <template #prepend>
                                <FontAwesomeIcon :icon="faEye" />
                            </template>
                            {{ t("General.view") }}
                        </v-btn>
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { faEye } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce } from "lodash-es";
import { type Ref, computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { InfodeskTransactionItem } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { useTableState } from "@/composables/useTableState";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{ eventId: string }>();
const { t } = useI18n();
const router = useRouter();
const toast = useToast();

const eventId = computed(() => parseInt(props.eventId, 10));

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    { title: t("InfodeskView.title"), disabled: true },
]);

const tableState = useTableState({ initialSort: { key: "id", order: "desc" } });
const totalItems = ref(0);
const items: Ref<InfodeskTransactionItem[]> = ref([]);
const itemsLoading = ref(false);

const itemHeaders = computed<ReadonlyHeaders>(() => [
    { title: t("InfodeskView.headers.itemName"), sortable: false, key: "item_name" },
    { title: t("InfodeskView.headers.key"), sortable: false, key: "key" },
    { title: t("InfodeskView.headers.customer"), sortable: false, key: "transaction_full_name" },
    { title: t("InfodeskView.headers.payment"), sortable: false, key: "transaction_is_paid" },
    { title: t("InfodeskView.headers.delivery"), sortable: false, key: "is_delivered" },
    { title: t("General.actions"), sortable: false, key: "actions", align: "end" },
]);

async function loadItems(args: LoadArgs) {
    itemsLoading.value = true;
    try {
        const response = await api.infodeskEventTransactionItemsList({
            path: { event_pk: eventId.value },
            query: getLoadArgs(args),
        });
        items.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("InfodeskView.loadFailure"));
        console.error(e);
    } finally {
        itemsLoading.value = false;
    }
}

const debouncedLoad = debounce(loadItems, 250);

function onTableOptionsUpdate(args: LoadArgs) {
    tableState.onOptionsUpdate(args);
    debouncedLoad(args);
}

function viewItem(id: number): void {
    router.push({ name: "infodesk-item", params: { eventId: props.eventId, id } });
}
</script>
