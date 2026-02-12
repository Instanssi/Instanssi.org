<template>
    <LayoutBase :key="`uploads-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.UPLOADED_FILE)"
                    color="primary"
                    @click="createItem"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("UploadsView.newUpload") }}
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
                    :no-data-text="t('UploadsView.noUploadsFound')"
                    :loading-text="t('UploadsView.loadingUploads')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.date="{ item }">
                        <DateTimeCell :value="item.date" />
                    </template>
                    <template #item.file="{ item }">
                        <MediaCell :url="item.file" class="upload-media-cell" />
                    </template>
                    <template #item.actions="{ item }">
                        <v-btn
                            icon
                            variant="text"
                            size="small"
                            :title="t('UploadsView.headers.file')"
                            @click="copyUrl(item.file)"
                        >
                            <FontAwesomeIcon :icon="faCopy" />
                        </v-btn>
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.UPLOADED_FILE)"
                            :can-delete="auth.canDelete(PermissionTarget.UPLOADED_FILE)"
                            :audit-log="{
                                appLabel: 'admin_upload',
                                model: 'uploadedfile',
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
import { faCopy, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, inject, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import * as api from "@/api";
import type { UploadedFile } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
import MediaCell from "@/components/table/MediaCell.vue";
import TableActionButtons from "@/components/table/TableActionButtons.vue";
import { useResponsiveHeaders } from "@/composables/useResponsiveHeaders";
import { useTableState } from "@/composables/useTableState";
import { getFilenameFromUrl } from "@/utils/media";
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
    { title: t("UploadsView.title"), disabled: true },
]);

const tableState = useTableState({ initialSort: { key: "date", order: "desc" } });
const totalItems = ref(0);
const items: Ref<UploadedFile[]> = ref([]);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const headers = useResponsiveHeaders(() => [
    {
        title: t("General.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("UploadsView.headers.date"),
        sortable: true,
        key: "date",
    },
    {
        title: t("UploadsView.headers.file"),
        sortable: false,
        key: "file",
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

async function copyUrl(url: string): Promise<void> {
    try {
        await navigator.clipboard.writeText(url);
        toast.success(t("UploadsView.copySuccess"));
    } catch {
        toast.error(t("UploadsView.copyFailure"));
    }
}

function flushData() {
    if (lastLoadArgs.value) {
        load(lastLoadArgs.value);
    }
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventUploadsFilesList({
            path: { event_pk: eventId.value },
            query: {
                ...getLoadArgs(args),
            },
        });
        items.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("UploadsView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

function onTableOptionsUpdate(args: LoadArgs) {
    tableState.onOptionsUpdate(args);
    debouncedLoad(args);
}

function refresh() {
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

async function deleteItem(item: UploadedFile): Promise<void> {
    const text = t("UploadsView.confirmDelete", {
        description: item.description || getFilenameFromUrl(item.file) || item.file,
    });
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventUploadsFilesDestroy({
                path: { event_pk: eventId.value, id: item.id },
            });
            toast.success(t("UploadsView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("UploadsView.deleteFailure")));
            console.error(e);
        }
    });
}

function editItem(id: number): void {
    router.push({
        name: "uploads-edit",
        params: { eventId: eventId.value, id },
        query: route.query,
    });
}

function createItem(): void {
    router.push({ name: "uploads-new", params: { eventId: eventId.value }, query: route.query });
}
</script>

<style scoped>
.upload-media-cell {
    margin: 3px 0;
}
</style>
