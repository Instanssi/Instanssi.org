<template>
    <LayoutBase :title="t('BlogEditorView.title')" :key="`blog-${eventId}`">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.BLOG_ENTRY)"
                    prepend-icon="fas fa-plus"
                    @click="createPost"
                >
                    {{ t("BlogEditorView.newBlogPost") }}
                </v-btn>
                <v-text-field
                    variant="outlined"
                    density="compact"
                    :label="t('General.search')"
                    style="max-width: 400px"
                    class="ma-0 pa-0 ml-4"
                    v-model="search"
                    clearable
                />
            </v-row>
        </v-col>
        <v-col>
            <v-row>
                <v-data-table-server
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :key="`blog-table-${refreshKey}`"
                    :headers="headers"
                    :items="blogPosts"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="search"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('BlogEditorView.noBlogPostsFound')"
                    :loading-text="t('BlogEditorView.loadingBlogPosts')"
                    v-model:items-per-page="perPage"
                    @update:options="debouncedLoad"
                >
                    <template v-slot:item.public="{ item }">
                        <v-icon v-if="item.public" icon="fas fa-check" color="green" />
                        <v-icon v-else icon="fas fa-xmark" color="red" />
                    </template>
                    <template v-slot:item.date="{ item }">
                        {{ d(item.date, "long") }}
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-btn
                            v-if="auth.canDelete(PermissionTarget.BLOG_ENTRY)"
                            density="compact"
                            variant="text"
                            @click="deletePost(item)"
                            prepend-icon="fas fa-xmark"
                            color="red"
                            >Delete</v-btn
                        >
                        <v-btn
                            v-if="auth.canChange(PermissionTarget.BLOG_ENTRY)"
                            density="compact"
                            variant="text"
                            @click="editPost(item.id)"
                            prepend-icon="fas fa-pen-to-square"
                            >Edit</v-btn
                        >
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
    <BlogPostDialog ref="dialog" />
</template>

<script setup lang="ts">
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, inject, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import type { VDataTableServer } from "vuetify/components";

import type { BlogEntry } from "@/api";
import BlogPostDialog from "@/components/BlogPostDialog.vue";
import LayoutBase from "@/components/LayoutBase.vue";
import { useAPI } from "@/services/api";
import { PermissionTarget, useAuth } from "@/services/auth";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";

// Get vuetify data-table headers type, It is not currently exported, so just fetch it by hand :)
type ReadonlyHeaders = InstanceType<typeof VDataTableServer>["headers"];

const props = defineProps<{ eventId: string }>();
const { t, d } = useI18n();

const dialog: Ref<InstanceType<typeof BlogPostDialog> | undefined> = ref(undefined);
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;

const toast = useToast();
const api = useAPI();
const auth = useAuth();
const eventId = computed(() => parseInt(props.eventId, 10));
const loading = ref(false);
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

async function load(args: LoadArgs) {
    loading.value = true;
    try {
        const { count, results } = await api.blogEntries.blogEntriesList({
            event: parseInt(props.eventId, 10),
            ...getLoadArgs(args),
        });
        blogPosts.value = results;
        totalItems.value = count;
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
    const ok = await confirmDialog.value!.confirm(text);
    if (ok) {
        try {
            await api.blogEntries.blogEntriesDestroy({ id: item.id });
            toast.success(t("BlogEditorView.deleteSuccess"));
        } catch (e) {
            toast.error(t("BlogEditorView.deleteFailure"));
            console.error(e);
        }
        refreshKey.value += 1;
    }
}

async function editPost(id: number): Promise<void> {
    const item = await api.blogEntries.blogEntriesRetrieve({ id });
    if (await dialog.value!.modal(eventId.value, item)) {
        refreshKey.value += 1;
    }
}

async function createPost() {
    if (await dialog.value!.modal(eventId.value)) {
        currentPage.value = 1;
        refreshKey.value += 1;
    }
}
</script>
