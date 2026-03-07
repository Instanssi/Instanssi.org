<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else-if="item">
            <v-row>
                <!-- Product Information -->
                <v-col cols="12" md="6">
                    <InfoCard :title="t('InfodeskItemView.sections.product')">
                        <InfoRow
                            :label="t('InfodeskItemView.labels.productName')"
                            :value="item.item_name"
                        />
                        <InfoRow
                            v-if="item.variant_name"
                            :label="t('InfodeskItemView.labels.variant')"
                            :value="item.variant_name"
                        />
                        <InfoRow :label="t('InfodeskItemView.labels.key')">
                            <code>{{ item.key }}</code>
                        </InfoRow>
                        <InfoRow :label="t('InfodeskItemView.labels.price')">
                            {{ item.purchase_price }} &euro;
                        </InfoRow>
                    </InfoCard>
                </v-col>

                <!-- Status -->
                <v-col cols="12" md="6">
                    <InfoCard :title="t('InfodeskItemView.sections.status')">
                        <InfoRow :label="t('InfodeskItemView.labels.payment')">
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
                        </InfoRow>
                        <InfoRow :label="t('InfodeskItemView.labels.delivery')">
                            <v-chip :color="item.is_delivered ? 'success' : 'warning'" size="small">
                                {{
                                    item.is_delivered
                                        ? formatDateTime(item.time_delivered)
                                        : t("InfodeskView.notDelivered")
                                }}
                            </v-chip>
                        </InfoRow>
                    </InfoCard>
                </v-col>
            </v-row>

            <v-row v-if="transaction">
                <v-col cols="12" md="6">
                    <InfoCard :title="t('InfodeskTransactionView.sections.customer')">
                        <InfoRow
                            :label="t('InfodeskTransactionView.labels.name')"
                            :value="transaction.full_name"
                        />
                        <InfoRow :label="t('General.email')" :value="transaction.email" />
                        <InfoRow
                            v-if="transaction.company"
                            :label="t('InfodeskTransactionView.labels.company')"
                            :value="transaction.company"
                        />
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
            </v-row>

            <v-row>
                <v-col cols="12">
                    <v-alert
                        v-if="item.is_delivered"
                        type="success"
                        density="compact"
                        variant="tonal"
                    >
                        {{ t("InfodeskItemView.alreadyDelivered") }}
                    </v-alert>
                    <v-alert
                        v-if="!item.transaction_is_paid"
                        type="warning"
                        density="compact"
                        variant="tonal"
                    >
                        {{ t("InfodeskItemView.notPaidWarning") }}
                    </v-alert>
                </v-col>
            </v-row>

            <v-row>
                <v-col>
                    <v-btn
                        v-if="
                            !item.is_delivered && auth.canChange(PermissionTarget.INFODESK_ACCESS)
                        "
                        color="primary"
                        :loading="marking"
                        class="mr-2"
                        @click="markDelivered"
                    >
                        <template #prepend>
                            <FontAwesomeIcon :icon="faCheck" />
                        </template>
                        {{ t("InfodeskItemView.markDelivered") }}
                    </v-btn>
                    <v-btn variant="text" @click="viewTransaction">
                        {{ t("InfodeskItemView.viewTransaction") }}
                    </v-btn>
                    <v-btn variant="text" @click="goBack">
                        {{ t("InfodeskItemView.backToSearch") }}
                    </v-btn>
                </v-col>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { faCheck } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, onMounted, ref, type Ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";

import * as api from "@/api";
import type { InfodeskTransaction, InfodeskTransactionItem } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import InfoCard from "@/components/table/InfoCard.vue";
import InfoRow from "@/components/table/InfoRow.vue";
import { PermissionTarget, useAuth } from "@/services/auth";

const props = defineProps<{ eventId: string; id: string }>();
const { t, d } = useI18n();
const router = useRouter();
const toast = useToast();
const auth = useAuth();

const loading = ref(false);
const marking = ref(false);
const eventId = computed(() => parseInt(props.eventId, 10));
const itemId = computed(() => parseInt(props.id, 10));
const item: Ref<InfodeskTransactionItem | null> = ref(null);
const transaction: Ref<InfodeskTransaction | null> = ref(null);

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const crumbs: BreadcrumbItem[] = [
        {
            title: t("InfodeskView.title"),
            to: { name: "infodesk", params: { eventId: props.eventId } },
        },
    ];
    if (item.value && transaction.value) {
        crumbs.push({
            title: `#${transaction.value.id}`,
            to: {
                name: "infodesk-transaction",
                params: { eventId: props.eventId, id: item.value.transaction },
            },
        });
    } else {
        crumbs.push({ title: "...", disabled: true });
    }
    crumbs.push({ title: item.value?.item_name ?? "...", disabled: true });
    return crumbs;
});

function formatDateTime(dateStr: string | null | undefined): string {
    if (!dateStr) return "-";
    return d(new Date(dateStr), "long");
}

async function loadItem() {
    loading.value = true;
    try {
        const response = await api.infodeskEventTransactionItemsRetrieve({
            path: { event_pk: eventId.value, id: itemId.value },
        });
        item.value = response.data!;
        const txResponse = await api.infodeskEventTransactionsRetrieve({
            path: { event_pk: eventId.value, id: item.value.transaction },
        });
        transaction.value = txResponse.data!;
    } catch (e) {
        toast.error(t("InfodeskItemView.loadFailure"));
        console.error(e);
        goBack();
    } finally {
        loading.value = false;
    }
}

async function markDelivered() {
    marking.value = true;
    try {
        const response = await api.infodeskEventTransactionItemsMarkDeliveredCreate({
            path: { event_pk: eventId.value, id: itemId.value },
        });
        item.value = response.data!;
        toast.success(t("InfodeskItemView.markSuccess"));
    } catch (e) {
        toast.error(t("InfodeskItemView.markFailure"));
        console.error(e);
    } finally {
        marking.value = false;
    }
}

function goBack() {
    router.push({ name: "infodesk", params: { eventId: props.eventId } });
}

function viewTransaction() {
    if (item.value) {
        router.push({
            name: "infodesk-transaction",
            params: { eventId: props.eventId, id: item.value.transaction },
        });
    }
}

onMounted(loadItem);
</script>
