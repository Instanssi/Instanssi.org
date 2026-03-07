<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else-if="transaction">
            <v-row>
                <!-- Customer Information -->
                <v-col cols="12" md="6">
                    <InfoCard :title="t('InfodeskTransactionView.sections.customer')">
                        <InfoRow
                            :label="t('InfodeskTransactionView.labels.name')"
                            :value="transaction.full_name"
                        />
                        <InfoRow
                            v-if="transaction.company"
                            :label="t('InfodeskTransactionView.labels.company')"
                            :value="transaction.company"
                        />
                        <InfoRow :label="t('General.email')" :value="transaction.email" />
                        <InfoRow
                            v-if="transaction.telephone"
                            :label="t('InfodeskTransactionView.labels.telephone')"
                            :value="transaction.telephone"
                        />
                        <InfoRow
                            v-if="transaction.mobile"
                            :label="t('InfodeskTransactionView.labels.mobile')"
                            :value="transaction.mobile"
                        />
                    </InfoCard>
                </v-col>

                <!-- Status -->
                <v-col cols="12" md="6">
                    <InfoCard :title="t('InfodeskTransactionView.sections.status')">
                        <InfoRow :label="t('General.status')">
                            <v-chip :color="statusColor" size="small">
                                {{ transaction.status_text }}
                            </v-chip>
                        </InfoRow>
                        <InfoRow
                            v-if="transaction.information"
                            :label="t('InfodeskTransactionView.labels.information')"
                            :value="transaction.information"
                        />
                    </InfoCard>
                </v-col>
            </v-row>

            <!-- Items -->
            <v-row>
                <v-col cols="12">
                    <v-card>
                        <v-card-title>
                            {{ t("InfodeskTransactionView.sections.items") }}
                        </v-card-title>
                        <v-card-text>
                            <v-data-table
                                :headers="itemHeaders"
                                :items="transactionItems"
                                :loading="itemsLoading"
                                density="compact"
                                class="elevation-0"
                            >
                                <template #item.transaction_is_paid="{ item }">
                                    <v-chip
                                        :color="item.transaction_is_paid ? 'success' : 'error'"
                                        size="small"
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
                                    >
                                        {{
                                            item.is_delivered
                                                ? formatDateTime(item.time_delivered)
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
                            </v-data-table>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <v-row>
                <v-col>
                    <v-btn variant="text" @click="goBack">
                        {{ t("InfodeskItemView.backToSearch") }}
                    </v-btn>
                </v-col>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { faEye } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, onMounted, ref, type Ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { InfodeskTransaction, InfodeskTransactionItem } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import InfoCard from "@/components/table/InfoCard.vue";
import InfoRow from "@/components/table/InfoRow.vue";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{ eventId: string; id: string }>();
const { t, d } = useI18n();
const router = useRouter();
const toast = useToast();

const loading = ref(false);
const itemsLoading = ref(false);
const eventId = computed(() => parseInt(props.eventId, 10));
const transactionId = computed(() => parseInt(props.id, 10));
const transaction: Ref<InfodeskTransaction | null> = ref(null);
const transactionItems: Ref<InfodeskTransactionItem[]> = ref([]);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: t("InfodeskView.title"),
        to: { name: "infodesk", params: { eventId: props.eventId } },
    },
    { title: transaction.value ? `#${transaction.value.id}` : "...", disabled: true },
]);

const statusColor = computed(() => {
    if (!transaction.value) return "grey";
    if (transaction.value.is_paid) return "success";
    if (transaction.value.is_cancelled) return "error";
    if (transaction.value.is_pending) return "warning";
    return "grey";
});

const itemHeaders = computed<ReadonlyHeaders>(() => [
    { title: t("InfodeskView.headers.itemName"), key: "item_name" },
    { title: t("InfodeskView.headers.key"), key: "key" },
    { title: t("InfodeskView.headers.payment"), key: "transaction_is_paid" },
    { title: t("InfodeskView.headers.delivery"), key: "is_delivered" },
    { title: t("General.actions"), key: "actions", align: "end" },
]);

function formatDateTime(dateStr: string | null | undefined): string {
    if (!dateStr) return "-";
    return d(new Date(dateStr), "long");
}

async function loadTransaction() {
    loading.value = true;
    try {
        const response = await api.infodeskEventTransactionsRetrieve({
            path: { event_pk: eventId.value, id: transactionId.value },
        });
        transaction.value = response.data!;
    } catch (e) {
        toast.error(t("InfodeskTransactionView.loadFailure"));
        console.error(e);
        goBack();
    } finally {
        loading.value = false;
    }
}

async function loadTransactionItems() {
    itemsLoading.value = true;
    try {
        const response = await api.infodeskEventTransactionItemsList({
            path: { event_pk: eventId.value },
            query: { transaction: transactionId.value, limit: 1000 },
        });
        transactionItems.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load transaction items:", e);
    } finally {
        itemsLoading.value = false;
    }
}

function viewItem(id: number): void {
    router.push({ name: "infodesk-item", params: { eventId: props.eventId, id } });
}

function goBack() {
    router.push({ name: "infodesk", params: { eventId: props.eventId } });
}

onMounted(async () => {
    await Promise.all([loadTransaction(), loadTransactionItems()]);
});
</script>
