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
import { inject, type Ref, ref } from "vue";
import { debounce } from "lodash-es";

import LayoutBase from "@/components/LayoutBase.vue";
import BlogPostDialog from "@/components/BlogPostDialog.vue";
import { useI18n } from "vue-i18n";
import { confirmDialogKey, type ConfirmDialogType } from "@/symbols";
import type { VDataTableServer } from "vuetify/components";
import { useAPI } from "@/services/api";
import type { BlogEntry } from "@/api";
import { PermissionTarget, useAuth } from "@/services/auth";

// Not exported by vuetify -- use our own.
type LoadArgs = {
    page: number;
    itemsPerPage: number;
    sortBy: any;
    groupBy: any;
    search: string;
};

// Get vuetify data-table headers type, It is not currently exported, so just fetch it by hand :)
type ReadonlyHeaders = InstanceType<typeof VDataTableServer>["headers"];

const props = defineProps<{ eventId: string }>();
const { t, d } = useI18n();

const dialog: Ref<InstanceType<typeof BlogPostDialog> | undefined> = ref(undefined);
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;

const api = useAPI();
const auth = useAuth();
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
    const limit = args.itemsPerPage;
    const offset = (args.page - 1) * limit;
    const { count, results } = await api.blogEntries.blogEntriesList(
        parseInt(props.eventId, 10),
        limit,
        offset,
        args.sortBy,
        args.search
    );
    blogPosts.value = results;
    totalItems.value = count;
    loading.value = false;
}

const debouncedLoad = debounce(load, 250); // Don't murderate the server API

async function deletePost(item: BlogEntry): Promise<void> {
    const text = t("BlogEditorView.confirmDelete", item);
    const ok = await confirmDialog.value!.confirm(text);
    if (ok) {
        await api.blogEntries.blogEntriesDestroy(item.id);
        refreshKey.value += 1;
    }
}

async function editPost(id: number): Promise<void> {
    const item = await api.blogEntries.blogEntriesRetrieve(id);
    const { ok, text, title, isPublic } = await dialog.value!.modal(item);
    if (ok) {
        await api.blogEntries.blogEntriesPartialUpdate(item.id, { title, text, public: isPublic });
        refreshKey.value += 1;
    }
}

async function createPost() {
    const { ok, text, title, isPublic } = await dialog.value!.modal();
    if (ok) {
        const event = parseInt(props.eventId, 10);
        await api.blogEntries.blogEntriesCreate({ event, title, text, public: isPublic });
        currentPage.value = 1;
        refreshKey.value += 1;
    }
}
</script>
