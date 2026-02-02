<template>
    <v-card v-if="hasPermission" variant="outlined" class="mt-4">
        <v-card-title class="d-flex align-center">
            <FontAwesomeIcon :icon="faClockRotateLeft" class="mr-2" />
            {{ t("AuditLogTable.title") }}
        </v-card-title>
        <v-card-text>
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
                @update:options="debouncedLoad"
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
        </v-card-text>
    </v-card>
</template>

<script setup lang="ts">
import { faClockRotateLeft } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce } from "lodash-es";
import { computed, type Ref, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { LogEntry } from "@/api";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
import DiffViewer from "@/components/auditlog/DiffViewer.vue";
import { PermissionTarget, useAuth } from "@/services/auth";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

interface LoadOptions {
    page: number;
    itemsPerPage: number;
    sortBy: { key: string; order: "asc" | "desc" }[];
}

const props = defineProps<{
    appLabel: string;
    model: string;
    objectPk?: string | number;
}>();

const { t } = useI18n();
const toast = useToast();
const auth = useAuth();

const hasPermission = computed(() => auth.canView(PermissionTarget.LOG_ENTRY));

const loading = ref(false);
const defaultPageSize = 10;
const pageSizeOptions = [defaultPageSize, 25, 50];
const perPage = ref(defaultPageSize);
const totalItems = ref(0);
const currentPage = ref(1);
const entries: Ref<LogEntry[]> = ref([]);
const expanded: Ref<string[]> = ref([]);

const headers: ReadonlyHeaders = [
    { title: "", key: "data-table-expand", width: 50 },
    { title: t("AuditLogTable.headers.timestamp"), key: "timestamp", sortable: true },
    { title: t("AuditLogTable.headers.user"), key: "actor", sortable: false },
    { title: t("AuditLogTable.headers.action"), key: "action", sortable: false, width: 100 },
    { title: t("AuditLogTable.headers.object"), key: "object_repr", sortable: false },
];

function actionLabel(action: number): string {
    switch (action) {
        case 0:
            return t("AuditLogTable.actions.create");
        case 1:
            return t("AuditLogTable.actions.update");
        case 2:
            return t("AuditLogTable.actions.delete");
        default:
            return t("AuditLogTable.actions.unknown");
    }
}

function actionColor(action: number): string {
    switch (action) {
        case 0:
            return "success";
        case 1:
            return "warning";
        case 2:
            return "error";
        default:
            return "grey";
    }
}

async function load(options: LoadOptions) {
    if (!hasPermission.value) return;

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
        entries.value = response.data!.results;
        totalItems.value = response.data!.count ?? 0;
    } catch (e) {
        toast.error(t("AuditLogTable.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

// Reload when props change
watch(
    () => [props.appLabel, props.model, props.objectPk],
    () => {
        currentPage.value = 1;
        debouncedLoad({
            page: 1,
            itemsPerPage: perPage.value ?? defaultPageSize,
            sortBy: [{ key: "timestamp", order: "desc" }],
        });
    },
    { immediate: true }
);
</script>
