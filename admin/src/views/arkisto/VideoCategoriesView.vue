<template>
    <LayoutBase :key="`video-categories-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.OTHER_VIDEO_CATEGORY)"
                    @click="createCategory"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("VideoCategoriesView.newCategory") }}
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
                    :no-data-text="t('VideoCategoriesView.noCategoriesFound')"
                    :loading-text="t('VideoCategoriesView.loadingCategories')"
                    @update:options="debouncedLoad"
                >
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.OTHER_VIDEO_CATEGORY)"
                            :can-delete="auth.canDelete(PermissionTarget.OTHER_VIDEO_CATEGORY)"
                            @edit="editCategory(item.id)"
                            @delete="deleteCategory(item)"
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
import type { OtherVideoCategory } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import TableActionButtons from "@/components/table/TableActionButtons.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";
import { getApiErrorMessage } from "@/utils/http";

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
    { title: t("VideoCategoriesView.title"), disabled: true },
]);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const items: Ref<OtherVideoCategory[]> = ref([]);
const search = ref("");
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const headers: ReadonlyHeaders = [
    {
        title: t("VideoCategoriesView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("VideoCategoriesView.headers.name"),
        sortable: true,
        key: "name",
    },
    {
        title: t("VideoCategoriesView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

function flushData() {
    if (lastLoadArgs.value) {
        load(lastLoadArgs.value);
    }
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventArkistoVideoCategoriesList({
            path: { event_pk: eventId.value },
            query: getLoadArgs(args),
        });
        items.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("VideoCategoriesView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

async function deleteCategory(item: OtherVideoCategory): Promise<void> {
    const text = t("VideoCategoriesView.confirmDelete", item);
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventArkistoVideoCategoriesDestroy({
                path: { event_pk: eventId.value, id: item.id },
            });
            toast.success(t("VideoCategoriesView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("VideoCategoriesView.deleteFailure")));
            console.error(e);
        }
    });
}

function editCategory(id: number): void {
    router.push({ name: "arkisto-categories-edit", params: { eventId: eventId.value, id } });
}

function createCategory(): void {
    router.push({ name: "arkisto-categories-new", params: { eventId: eventId.value } });
}
</script>
