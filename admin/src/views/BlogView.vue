<template>
    <LayoutBase :key="`blog-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn v-if="auth.canAdd(PermissionTarget.BLOG_ENTRY)" @click="createPost">
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("BlogEditorView.newBlogPost") }}
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
                    :key="`blog-table-${refreshKey}`"
                    v-model:items-per-page="perPage"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="headers"
                    :items="blogPosts"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="search"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('BlogEditorView.noBlogPostsFound')"
                    :loading-text="t('BlogEditorView.loadingBlogPosts')"
                    @update:options="debouncedLoad"
                >
                    <template #item.public="{ item }">
                        <FontAwesomeIcon v-if="item.public" :icon="faCheck" class="text-green" />
                        <FontAwesomeIcon v-else :icon="faXmark" class="text-red" />
                    </template>
                    <template #item.date="{ item }">
                        {{ d(item.date, "long") }}
                    </template>
                    <template #item.actions="{ item }">
                        <v-btn
                            v-if="auth.canDelete(PermissionTarget.BLOG_ENTRY)"
                            density="compact"
                            variant="text"
                            color="red"
                            @click="deletePost(item)"
                        >
                            <template #prepend>
                                <FontAwesomeIcon :icon="faXmark" />
                            </template>
                            Delete
                        </v-btn>
                        <v-btn
                            v-if="auth.canChange(PermissionTarget.BLOG_ENTRY)"
                            density="compact"
                            variant="text"
                            @click="editPost(item.id)"
                        >
                            <template #prepend>
                                <FontAwesomeIcon :icon="faPenToSquare" />
                            </template>
                            Edit
                        </v-btn>
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { faCheck, faPenToSquare, faPlus, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, inject, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTableServer, VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { BlogEntry } from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/LayoutBase.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";
import { sleep } from "@/utils/sleep.ts";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const props = defineProps<{ eventId: string }>();
const { t, d } = useI18n();
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
    { title: t("BlogEditorView.title"), disabled: true },
]);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const blogPosts: Ref<BlogEntry[]> = ref([]);
const search = ref("");
const refreshKey = ref(0);
const headers: ReadonlyHeaders = [
    {
        title: t("BlogEditorView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("BlogEditorView.headers.title"),
        sortable: false,
        key: "title",
    },
    {
        title: t("BlogEditorView.headers.createdAt"),
        sortable: true,
        key: "date",
    },
    {
        title: t("BlogEditorView.headers.createdBy"),
        sortable: true,
        key: "created_by",
    },
    {
        title: t("BlogEditorView.headers.isPublic"),
        sortable: false,
        key: "public",
    },
    {
        title: t("BlogEditorView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

function flushData() {
    refreshKey.value += 1;
}

async function load(args: LoadArgs) {
    loading.value = true;
    try {
        const response = await api.adminBlogList({
            query: {
                event: parseInt(props.eventId, 10),
                ...getLoadArgs(args),
            },
        });
        blogPosts.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("BlogEditorView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250); // Don't murderate the server API

async function deletePost(item: BlogEntry): Promise<void> {
    const text = t("BlogEditorView.confirmDelete", item);
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await sleep(250);
            await api.adminBlogDestroy({ path: { id: item.id } });
            toast.success(t("BlogEditorView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(t("BlogEditorView.deleteFailure"));
            console.error(e);
        }
    });
}

function editPost(id: number): void {
    router.push({ name: "blog-edit", params: { eventId: eventId.value, id } });
}

function createPost(): void {
    router.push({ name: "blog-new", params: { eventId: eventId.value } });
}
</script>
