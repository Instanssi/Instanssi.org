<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else-if="transaction">
            <v-row>
                <!-- Customer Information -->
                <v-col cols="12" md="6">
                    <v-card>
                        <v-card-title>
                            {{ t("TransactionDetailView.sections.customer") }}
                        </v-card-title>
                        <v-card-text>
                            <v-table density="compact">
                                <tbody>
                                    <tr>
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.firstname") }}
                                        </td>
                                        <td>{{ transaction.firstname }}</td>
                                    </tr>
                                    <tr>
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.lastname") }}
                                        </td>
                                        <td>{{ transaction.lastname }}</td>
                                    </tr>
                                    <tr v-if="transaction.company">
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.company") }}
                                        </td>
                                        <td>{{ transaction.company }}</td>
                                    </tr>
                                    <tr>
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.email") }}
                                        </td>
                                        <td>{{ transaction.email }}</td>
                                    </tr>
                                    <tr v-if="transaction.telephone">
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.telephone") }}
                                        </td>
                                        <td>{{ transaction.telephone }}</td>
                                    </tr>
                                    <tr v-if="transaction.mobile">
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.mobile") }}
                                        </td>
                                        <td>{{ transaction.mobile }}</td>
                                    </tr>
                                </tbody>
                            </v-table>
                        </v-card-text>
                    </v-card>
                </v-col>

                <!-- Address -->
                <v-col cols="12" md="6">
                    <v-card>
                        <v-card-title>
                            {{ t("TransactionDetailView.sections.address") }}
                        </v-card-title>
                        <v-card-text>
                            <v-table density="compact">
                                <tbody>
                                    <tr>
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.street") }}
                                        </td>
                                        <td>{{ transaction.street }}</td>
                                    </tr>
                                    <tr>
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.postalcode") }}
                                        </td>
                                        <td>{{ transaction.postalcode }}</td>
                                    </tr>
                                    <tr>
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.city") }}
                                        </td>
                                        <td>{{ transaction.city }}</td>
                                    </tr>
                                    <tr v-if="transaction.country">
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.country") }}
                                        </td>
                                        <td>{{ transaction.country }}</td>
                                    </tr>
                                </tbody>
                            </v-table>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <v-row>
                <!-- Status -->
                <v-col cols="12" md="6">
                    <v-card>
                        <v-card-title>
                            {{ t("TransactionDetailView.sections.status") }}
                        </v-card-title>
                        <v-card-text>
                            <v-table density="compact">
                                <tbody>
                                    <tr>
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.timeCreated") }}
                                        </td>
                                        <td>
                                            {{ formatDateTime(transaction.time_created) }}
                                            <v-chip
                                                v-if="
                                                    transaction.time_created &&
                                                    !transaction.time_pending &&
                                                    !transaction.time_paid &&
                                                    !transaction.time_cancelled
                                                "
                                                color="grey"
                                                size="small"
                                                class="ml-2"
                                            >
                                                {{ t("TransactionsView.statuses.created") }}
                                            </v-chip>
                                        </td>
                                    </tr>
                                    <tr v-if="transaction.time_pending">
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.timePending") }}
                                        </td>
                                        <td>
                                            {{ formatDateTime(transaction.time_pending) }}
                                            <v-chip color="warning" size="small" class="ml-2">
                                                {{ t("TransactionsView.statuses.pending") }}
                                            </v-chip>
                                        </td>
                                    </tr>
                                    <tr v-if="transaction.time_paid">
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.timePaid") }}
                                        </td>
                                        <td>
                                            {{ formatDateTime(transaction.time_paid) }}
                                            <v-chip color="success" size="small" class="ml-2">
                                                {{ t("TransactionsView.statuses.paid") }}
                                            </v-chip>
                                        </td>
                                    </tr>
                                    <tr v-if="transaction.time_cancelled">
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.timeCancelled") }}
                                        </td>
                                        <td>
                                            {{ formatDateTime(transaction.time_cancelled) }}
                                            <v-chip color="error" size="small" class="ml-2">
                                                {{ t("TransactionsView.statuses.cancelled") }}
                                            </v-chip>
                                        </td>
                                    </tr>
                                </tbody>
                            </v-table>
                        </v-card-text>
                    </v-card>
                </v-col>

                <!-- Payment Details -->
                <v-col cols="12" md="6">
                    <v-card>
                        <v-card-title>
                            {{ t("TransactionDetailView.sections.payment") }}
                        </v-card-title>
                        <v-card-text>
                            <v-table density="compact">
                                <tbody>
                                    <tr v-if="transaction.payment_method_name">
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.paymentMethod") }}
                                        </td>
                                        <td>{{ transaction.payment_method_name }}</td>
                                    </tr>
                                    <tr>
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.total") }}
                                        </td>
                                        <td>{{ transaction.total_price }} &euro;</td>
                                    </tr>
                                    <tr>
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.key") }}
                                        </td>
                                        <td>
                                            <code>{{ transaction.key }}</code>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.token") }}
                                        </td>
                                        <td>
                                            <code>{{ transaction.token }}</code>
                                        </td>
                                    </tr>
                                    <tr v-if="transaction.information">
                                        <td class="font-weight-bold">
                                            {{ t("TransactionDetailView.labels.information") }}
                                        </td>
                                        <td>{{ transaction.information }}</td>
                                    </tr>
                                </tbody>
                            </v-table>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Items -->
            <v-row>
                <v-col cols="12">
                    <v-card>
                        <v-card-title>
                            {{ t("TransactionDetailView.sections.items") }}
                        </v-card-title>
                        <v-card-text>
                            <v-data-table
                                :headers="itemHeaders"
                                :items="transactionItems"
                                :loading="itemsLoading"
                                density="compact"
                                class="elevation-0"
                            >
                                <template #item.item="{ item }">
                                    {{ getItemName(item.item) }}
                                </template>
                                <template #item.variant="{ item }">
                                    {{ getVariantName(item.item, item.variant) }}
                                </template>
                                <template #item.purchase_price="{ item }">
                                    {{ item.purchase_price }} &euro;
                                </template>
                                <template #item.is_delivered="{ item }">
                                    <v-chip v-if="item.is_delivered" color="success" size="small">
                                        {{ formatDateTime(item.time_delivered) }}
                                    </v-chip>
                                    <span v-else>-</span>
                                </template>
                            </v-data-table>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Receipts -->
            <v-row>
                <v-col cols="12">
                    <v-card>
                        <v-card-title>
                            {{ t("TransactionDetailView.sections.receipts") }}
                        </v-card-title>
                        <v-card-text>
                            <div v-if="transaction.receipts.length === 0" class="text-grey">
                                {{ t("TransactionDetailView.receipts.noReceipts") }}
                            </div>
                            <v-table v-else density="compact">
                                <thead>
                                    <tr>
                                        <th>{{ t("TransactionDetailView.receipts.subject") }}</th>
                                        <th>{{ t("TransactionDetailView.receipts.to") }}</th>
                                        <th>{{ t("TransactionDetailView.receipts.from") }}</th>
                                        <th>{{ t("TransactionDetailView.receipts.sent") }}</th>
                                        <th></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="receipt in transaction.receipts" :key="receipt.id">
                                        <td>{{ receipt.subject }}</td>
                                        <td>{{ receipt.mail_to }}</td>
                                        <td>{{ receipt.mail_from }}</td>
                                        <td>
                                            <v-chip
                                                :color="receipt.is_sent ? 'success' : 'grey'"
                                                size="small"
                                            >
                                                {{
                                                    receipt.is_sent
                                                        ? formatDateTime(receipt.sent)
                                                        : t(
                                                              "TransactionDetailView.receipts.notSent"
                                                          )
                                                }}
                                            </v-chip>
                                        </td>
                                        <td>
                                            <v-btn
                                                v-if="auth.canChange(PermissionTarget.RECEIPT)"
                                                size="small"
                                                variant="text"
                                                :loading="resendingReceiptId === receipt.id"
                                                @click="resendReceipt(receipt.id)"
                                            >
                                                <template #prepend>
                                                    <FontAwesomeIcon :icon="faPaperPlane" />
                                                </template>
                                                {{ t("TransactionDetailView.receipts.resend") }}
                                            </v-btn>
                                        </td>
                                    </tr>
                                </tbody>
                            </v-table>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Event Log -->
            <v-row>
                <v-col cols="12">
                    <v-card>
                        <v-card-title>
                            {{ t("TransactionDetailView.sections.events") }}
                        </v-card-title>
                        <v-card-text>
                            <div v-if="transaction.events.length === 0" class="text-grey">
                                {{ t("TransactionDetailView.events.noEvents") }}
                            </div>
                            <v-table v-else density="compact">
                                <thead>
                                    <tr>
                                        <th>{{ t("TransactionDetailView.events.time") }}</th>
                                        <th>{{ t("TransactionDetailView.events.message") }}</th>
                                        <th>{{ t("TransactionDetailView.events.data") }}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="event in transaction.events" :key="event.id">
                                        <td>{{ formatDateTime(event.created) }}</td>
                                        <td>{{ event.message }}</td>
                                        <td>
                                            <code v-if="event.data" class="text-caption">
                                                {{ JSON.stringify(event.data) }}
                                            </code>
                                            <span v-else class="text-grey">-</span>
                                        </td>
                                    </tr>
                                </tbody>
                            </v-table>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <v-row>
                <v-col>
                    <v-btn variant="text" @click="goBack">
                        {{ t("General.cancel") }}
                    </v-btn>
                </v-col>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { faPaperPlane } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { parseInt } from "lodash-es";
import { computed, onMounted, ref, type Ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { StoreTransaction, StoreItem, TransactionItem } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{
    eventId: string;
    id: string;
}>();

const { t, d } = useI18n();
const router = useRouter();
const toast = useToast();
const { getEventById } = useEvents();
const auth = useAuth();

const loading = ref(false);
const itemsLoading = ref(false);
const resendingReceiptId = ref<number | null>(null);
const eventId = computed(() => parseInt(props.eventId, 10));
const transactionId = computed(() => parseInt(props.id, 10));
const transaction: Ref<StoreTransaction | null> = ref(null);
const transactionItems: Ref<TransactionItem[]> = ref([]);
const storeItems: Ref<StoreItem[]> = ref([]);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [
    {
        title: getEventById(eventId.value)?.name ?? "...",
        to: { name: "dashboard", params: { eventId: props.eventId } },
    },
    {
        title: t("TransactionsView.title"),
        to: { name: "store-transactions", params: { eventId: props.eventId } },
    },
    {
        title: transaction.value ? `#${transaction.value.id}` : "...",
        disabled: true,
    },
]);

const itemHeaders: ReadonlyHeaders = [
    {
        title: t("TransactionDetailView.items.name"),
        key: "item",
    },
    {
        title: t("TransactionDetailView.items.variant"),
        key: "variant",
    },
    {
        title: t("TransactionDetailView.items.price"),
        key: "purchase_price",
    },
    {
        title: t("TransactionDetailView.items.key"),
        key: "key",
    },
    {
        title: t("TransactionDetailView.items.delivered"),
        key: "is_delivered",
    },
];

function formatDateTime(dateStr: string | null | undefined): string {
    if (!dateStr) return "-";
    return d(new Date(dateStr), "long");
}

function getItemName(itemId: number): string {
    const item = storeItems.value.find((i) => i.id === itemId);
    return item?.name ?? `#${itemId}`;
}

function getVariantName(itemId: number, variantId: number | null | undefined): string {
    if (!variantId) return "-";
    const item = storeItems.value.find((i) => i.id === itemId);
    if (!item) return `#${variantId}`;
    const variant = item.variants?.find((v) => v.id === variantId);
    return variant?.name ?? `#${variantId}`;
}

async function resendReceipt(receiptId: number) {
    const receipt = transaction.value?.receipts.find((r) => r.id === receiptId);
    if (!receipt) return;

    resendingReceiptId.value = receiptId;
    try {
        await api.adminEventStoreReceiptsResendCreate({
            path: { event_pk: eventId.value, id: receiptId },
            body: {
                subject: receipt.subject,
                mail_to: receipt.mail_to,
                mail_from: receipt.mail_from,
            },
        });
        toast.success(t("TransactionDetailView.receipts.resendSuccess"));
        // Reload transaction to update receipt status
        await loadTransaction();
    } catch (e) {
        toast.error(t("TransactionDetailView.receipts.resendFailure"));
        console.error(e);
    } finally {
        resendingReceiptId.value = null;
    }
}

function goBack() {
    router.push({ name: "store-transactions", params: { eventId: props.eventId } });
}

async function loadTransaction() {
    loading.value = true;
    try {
        const response = await api.adminEventStoreTransactionsRetrieve({
            path: { event_pk: eventId.value, id: transactionId.value },
        });
        transaction.value = response.data!;
    } catch (e) {
        toast.error(t("TransactionDetailView.loadFailure"));
        console.error(e);
        goBack();
    } finally {
        loading.value = false;
    }
}

async function loadTransactionItems() {
    itemsLoading.value = true;
    try {
        const response = await api.adminEventStoreTransactionItemsList({
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

async function loadStoreItems() {
    try {
        const response = await api.adminEventStoreItemsList({
            path: { event_pk: eventId.value },
            query: { limit: 1000 },
        });
        storeItems.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load store items:", e);
    }
}

onMounted(async () => {
    await Promise.all([loadTransaction(), loadStoreItems()]);
    await loadTransactionItems();
});
</script>
