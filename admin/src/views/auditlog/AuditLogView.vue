<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row class="align-center">
                <v-select
                    v-model="selectedModel"
                    variant="outlined"
                    density="compact"
                    :label="t('AuditLogView.filterByModel')"
                    :items="modelOptions"
                    item-title="label"
                    item-value="value"
                    style="max-width: 300px"
                    class="ma-0 pa-0"
                    clearable
                    @update:model-value="onFilterChange"
                />
            </v-row>
        </v-col>
        <v-col>
            <v-row>
                <v-data-table-server
                    v-model:items-per-page="perPage"
                    v-model:expanded="expanded"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="headers"
                    :items="entries"
                    :items-length="totalItems"
                    :loading="loading"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('AuditLogView.noEntriesFound')"
                    :loading-text="t('AuditLogView.loadingEntries')"
                    show-expand
                    @update:options="debouncedLoad"
                >
                    <template #item.timestamp="{ item }">
                        <DateTimeCell :value="item.timestamp" />
                    </template>
                    <template #item.actor="{ item }">
                        {{ item.actor?.username ?? t("AuditLogView.system") }}
                    </template>
                    <template #item.action="{ item }">
                        <v-chip :color="actionColor(item.action)" size="small" variant="tonal">
                            {{ actionLabel(item.action) }}
                        </v-chip>
                    </template>
                    <template #item.content_type="{ item }">
                        {{ item.content_type?.app_label }}.{{ item.content_type?.model }}
                    </template>
                    <template #item.object_repr="{ item }">
                        <span class="text-truncate" style="max-width: 300px; display: inline-block">
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
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { debounce } from "lodash-es";
import { type Ref, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { LogEntry } from "@/api";
import DiffViewer from "@/components/auditlog/DiffViewer.vue";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

interface LoadOptions {
    page: number;
    itemsPerPage: number;
    sortBy: { key: string; order: "asc" | "desc" }[];
}

interface ModelOption {
    label: string;
    value: string; // format: "app_label.model"
}

const { t } = useI18n();
const toast = useToast();

const breadcrumbs: BreadcrumbItem[] = [{ title: t("AuditLogView.title"), disabled: true }];

// Available models for filtering
const modelOptions: ModelOption[] = [
    { label: t("AuditLogView.models.user"), value: "users.user" },
    { label: t("AuditLogView.models.event"), value: "kompomaatti.event" },
    { label: t("AuditLogView.models.blogEntry"), value: "ext_blog.blogentry" },
    { label: t("AuditLogView.models.programmeEvent"), value: "ext_programme.programmeevent" },
    { label: t("AuditLogView.models.compo"), value: "kompomaatti.compo" },
    { label: t("AuditLogView.models.entry"), value: "kompomaatti.entry" },
    { label: t("AuditLogView.models.competition"), value: "kompomaatti.competition" },
    {
        label: t("AuditLogView.models.competitionParticipation"),
        value: "kompomaatti.competitionparticipation",
    },
    { label: t("AuditLogView.models.storeItem"), value: "store.storeitem" },
    { label: t("AuditLogView.models.storeTransaction"), value: "store.storetransaction" },
    { label: t("AuditLogView.models.uploadedFile"), value: "admin_upload.uploadedfile" },
    { label: t("AuditLogView.models.otherVideo"), value: "arkisto.othervideo" },
    { label: t("AuditLogView.models.otherVideoCategory"), value: "arkisto.othervideocategory" },
];

const loading = ref(false);
const defaultPageSize = 25;
const pageSizeOptions = [defaultPageSize, 50, 100];
const perPage = ref(defaultPageSize);
const totalItems = ref(0);
const currentPage = ref(1);
const entries: Ref<LogEntry[]> = ref([]);
const expanded: Ref<string[]> = ref([]);
const selectedModel = ref<string | null>(null);
const lastLoadOptions: Ref<LoadOptions | null> = ref(null);

const headers: ReadonlyHeaders = [
    { title: "", key: "data-table-expand", width: 50 },
    {
        title: t("AuditLogView.headers.timestamp"),
        key: "timestamp",
        sortable: true,
    },
    {
        title: t("AuditLogView.headers.user"),
        key: "actor",
        sortable: false,
    },
    {
        title: t("AuditLogView.headers.action"),
        key: "action",
        sortable: false,
        width: 100,
    },
    {
        title: t("AuditLogView.headers.model"),
        key: "content_type",
        sortable: false,
    },
    {
        title: t("AuditLogView.headers.object"),
        key: "object_repr",
        sortable: false,
    },
];

function actionLabel(action: number): string {
    switch (action) {
        case 0:
            return t("AuditLogView.actions.create");
        case 1:
            return t("AuditLogView.actions.update");
        case 2:
            return t("AuditLogView.actions.delete");
        default:
            return t("AuditLogView.actions.unknown");
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

function onFilterChange() {
    // Reset to page 1 when filter changes
    currentPage.value = 1;
    if (lastLoadOptions.value) {
        load({ ...lastLoadOptions.value, page: 1 });
    }
}

async function load(options: LoadOptions) {
    loading.value = true;
    lastLoadOptions.value = options;
    try {
        const query: api.AdminAuditlogListData["query"] = {
            limit: options.itemsPerPage,
            offset: (options.page - 1) * options.itemsPerPage,
        };

        // Add model filter if selected
        if (selectedModel.value) {
            const [appLabel, model] = selectedModel.value.split(".");
            query.app_label = appLabel;
            query.model = model;
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
        toast.error(t("AuditLogView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);
</script>
