<template>
    <LayoutBase :key="`videos-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn v-if="auth.canAdd(PermissionTarget.OTHER_VIDEO)" @click="createVideo">
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("VideosView.newVideo") }}
                </v-btn>
                <v-select
                    v-model="selectedCategory"
                    :items="categoryOptions"
                    variant="outlined"
                    density="compact"
                    :label="t('VideosView.filterByCategory')"
                    style="max-width: 300px"
                    class="ma-0 pa-0 ml-4"
                    clearable
                />
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
                    :key="`videos-table-${refreshKey}`"
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
                    :no-data-text="t('VideosView.noVideosFound')"
                    :loading-text="t('VideosView.loadingVideos')"
                    @update:options="debouncedLoad"
                >
                    <template #item.category="{ item }">
                        {{ getCategoryName(item.category) }}
                    </template>
                    <template #item.youtube_url="{ item }">
                        <a
                            v-if="item.youtube_url"
                            :href="getYoutubeUrl(item.youtube_url)"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            {{ formatYoutubeUrl(item.youtube_url) }}
                        </a>
                        <span v-else>-</span>
                    </template>
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.OTHER_VIDEO)"
                            :can-delete="auth.canDelete(PermissionTarget.OTHER_VIDEO)"
                            @edit="editVideo(item.id)"
                            @delete="deleteVideo(item)"
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
import { type Ref, computed, inject, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { OtherVideo, OtherVideoCategory } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
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
    { title: t("VideosView.title"), disabled: true },
]);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const items: Ref<OtherVideo[]> = ref([]);
const categories: Ref<OtherVideoCategory[]> = ref([]);
const search = ref("");
const selectedCategory: Ref<number | null> = ref(null);
const refreshKey = ref(0);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);

const headers: ReadonlyHeaders = [
    {
        title: t("VideosView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("VideosView.headers.name"),
        sortable: true,
        key: "name",
    },
    {
        title: t("VideosView.headers.category"),
        sortable: false,
        key: "category",
    },
    {
        title: t("VideosView.headers.youtube"),
        sortable: false,
        key: "youtube_url",
    },
    {
        title: t("VideosView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

const categoryOptions = computed(() => [
    { title: t("VideosView.allCategories"), value: null },
    ...categories.value.map((c) => ({ title: c.name, value: c.id })),
]);

function getCategoryName(categoryId: number): string {
    const category = categories.value.find((c) => c.id === categoryId);
    return category?.name ?? `#${categoryId}`;
}

function getYoutubeUrl(youtube_url: { video_id: string; start?: number | null }): string {
    let url = `https://www.youtube.com/watch?v=${youtube_url.video_id}`;
    if (youtube_url.start) {
        url += `&t=${youtube_url.start}`;
    }
    return url;
}

function formatYoutubeUrl(youtube_url: { video_id: string; start?: number | null }): string {
    if (youtube_url.start) {
        return `${youtube_url.video_id} (t=${youtube_url.start}s)`;
    }
    return youtube_url.video_id;
}

function flushData() {
    refreshKey.value += 1;
}

async function loadCategories() {
    try {
        const response = await api.adminEventArkistoVideoCategoriesList({
            path: { event_pk: eventId.value },
            query: { limit: 100 },
        });
        categories.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load categories:", e);
    }
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminEventArkistoVideosList({
            path: { event_pk: eventId.value },
            query: {
                ...getLoadArgs(args),
                ...(selectedCategory.value ? { category: selectedCategory.value } : {}),
            },
        });
        items.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("VideosView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

// Reload when category filter changes
watch(selectedCategory, () => {
    if (lastLoadArgs.value) {
        debouncedLoad(lastLoadArgs.value);
    }
});

async function deleteVideo(item: OtherVideo): Promise<void> {
    const text = t("VideosView.confirmDelete", item);
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventArkistoVideosDestroy({
                path: { event_pk: eventId.value, id: item.id },
            });
            toast.success(t("VideosView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(t("VideosView.deleteFailure"));
            console.error(e);
        }
    });
}

function editVideo(id: number): void {
    router.push({ name: "arkisto-videos-edit", params: { eventId: eventId.value, id } });
}

function createVideo(): void {
    router.push({ name: "arkisto-videos-new", params: { eventId: eventId.value } });
}

onMounted(() => {
    loadCategories();
});
</script>
