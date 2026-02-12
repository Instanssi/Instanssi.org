<template>
    <ContentDialog
        v-model="dialogVisible"
        :title="t('AuditLogTable.title')"
        :max-width="900"
        :scrollable="true"
        content-class="pa-0"
    >
        <template #default>
            <v-data-table-server
                v-model:items-per-page="perPage"
                v-model:expanded="expanded"
                class="elevation-0"
                item-value="id"
                density="compact"
                :headers="headers"
                :items="entries"
                :items-length="totalItems"
                :loading="loading"
                :page="currentPage"
                :items-per-page-options="pageSizeOptions"
                :no-data-text="t('AuditLogTable.noEntriesFound')"
                :loading-text="t('AuditLogTable.loadingEntries')"
                show-expand
                @update:options="loadData"
            >
                <template #item.timestamp="{ item }">
                    <DateTimeCell :value="item.timestamp" />
                </template>
                <template #item.actor="{ item }">
                    {{ item.actor?.username ?? t("AuditLogTable.system") }}
                </template>
                <template #item.action="{ item }">
                    <v-chip :color="actionColor(item.action)" size="small" variant="tonal">
                        {{ actionLabel(item.action) }}
                    </v-chip>
                </template>
                <template #item.object_repr="{ item }">
                    <span class="text-truncate" style="max-width: 200px; display: inline-block">
                        {{ item.object_repr }}
                    </span>
                </template>
                <template #expanded-row="{ columns, item }">
                    <tr>
                        <td :colspan="columns.length" class="pa-4 bg-grey-lighten-4">
                            <DiffViewer :changes="item.changes" />
                        </td>
                    </tr>
                </template>
            </v-data-table-server>
        </template>
    </ContentDialog>
</template>

<script setup lang="ts">
import { type Ref, computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { LogEntry } from "@/api";
import DiffViewer from "@/components/auditlog/DiffViewer.vue";
import ContentDialog from "@/components/dialogs/ContentDialog.vue";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
import { type LoadOptions, useAuditLogUtils } from "@/composables/useAuditLogUtils";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{
    appLabel: string;
    model: string;
    objectPk?: string | number;
}>();

const dialogVisible = defineModel<boolean>({ default: false });

const { t } = useI18n();
const toast = useToast();
const { actionLabel, actionColor } = useAuditLogUtils();

const loading = ref(false);
const defaultPageSize = 10;
const pageSizeOptions = [defaultPageSize, 25, 50];
const perPage = ref(defaultPageSize);
const totalItems = ref(0);
const currentPage = ref(1);
const entries: Ref<LogEntry[]> = ref([]);
const expanded: Ref<string[]> = ref([]);

const headers = computed<ReadonlyHeaders>(() => [
    { title: "", key: "data-table-expand", width: 50 },
    { title: t("AuditLogTable.headers.timestamp"), key: "timestamp", sortable: true },
    { title: t("AuditLogTable.headers.user"), key: "actor", sortable: false },
    { title: t("AuditLogTable.headers.action"), key: "action", sortable: false, width: 100 },
    { title: t("AuditLogTable.headers.object"), key: "object_repr", sortable: false },
]);

async function loadData(options: LoadOptions) {
    loading.value = true;
    try {
        const query: api.AdminAuditlogListData["query"] = {
            app_label: props.appLabel,
            model: props.model,
            limit: options.itemsPerPage,
            offset: (options.page - 1) * options.itemsPerPage,
        };

        if (props.objectPk !== undefined) {
            query.object_pk = String(props.objectPk);
        }

        if (options.sortBy.length > 0) {
            const sort = options.sortBy[0];
            if (sort) {
                query.ordering = sort.order === "desc" ? `-${sort.key}` : sort.key;
            }
        }

        const response = await api.adminAuditlogList({ query });
        entries.value = response.data?.results ?? [];
        totalItems.value = response.data?.count ?? 0;
    } catch (e) {
        toast.error(t("AuditLogTable.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

// Load data when dialog opens
watch(dialogVisible, (visible) => {
    if (visible) {
        currentPage.value = 1;
        loadData({
            page: 1,
            itemsPerPage: perPage.value ?? defaultPageSize,
            sortBy: [{ key: "timestamp", order: "desc" }],
        });
    }
});
</script>
