<template>
    <LayoutBase title="Blog" :key="`blog-${eventId}`">
        <v-col>
            <v-row>
                <v-btn prepend-icon="fas fa-plus" @click="create"> New blog post </v-btn>
                <v-text-field
                    variant="outlined"
                    density="compact"
                    label="Search"
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
                    :key="`blog-table-${refreshKey}`"
                    :headers="headers"
                    :items="blogPosts"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="search"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    v-model:items-per-page="perPage"
                    @update:options="debouncedLoad"
                >
                    <template v-slot:item.public="{ item }">
                        <v-icon v-if="item.public" icon="fas fa-check" color="green" />
                        <v-icon v-else icon="fas fa-xmark" color="red" />
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
    <BlogPostDialog ref="dialog" />
</template>

<script setup lang="ts">
import { type Ref, ref } from "vue";
import { debounce } from "lodash-es";

import LayoutBase from "@/components/LayoutBase.vue";
import BlogPostDialog from "@/components/BlogPostDialog.vue";
import { useAPI } from "@/apis";
import type { BlogPost } from "@/apis/blog_api";

// Not exported by vuetify -- use our own.
type LoadArgs = {
    page: number;
    itemsPerPage: number;
    sortBy: any;
    groupBy: any;
    search: string;
};

const props = defineProps<{ eventId: string }>();

const dialog: Ref<InstanceType<typeof BlogPostDialog> | undefined> = ref(undefined);

const api = useAPI();
const loading = ref(false);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const blogPosts: Ref<BlogPost[]> = ref([]);
const search = ref("");
const refreshKey = ref(0);
const headers = [
    {
        title: "ID",
        sortable: true,
        key: "id",
    },
    {
        title: "Title",
        sortable: false,
        key: "title",
    },
    {
        title: "Created at",
        sortable: true,
        key: "date",
    },
    {
        title: "Created by",
        sortable: true,
        key: "user",
    },
    {
        title: "Public",
        sortable: false,
        key: "public",
    },
];

async function load(args: LoadArgs) {
    loading.value = true;
    const limit = args.itemsPerPage;
    const offset = (args.page - 1) * limit;
    const { count, results } = await api.blog.getBlogEntries(
        { event: parseInt(props.eventId, 10) },
        offset,
        limit,
        args.search,
        args.sortBy
    );
    blogPosts.value = results;
    totalItems.value = count;
    loading.value = false;
}

const debouncedLoad = debounce(load, 500); // Don't murderate the server API

async function create() {
    const { ok, text, title, isPublic } = await dialog.value!.modal();
    const event = parseInt(props.eventId, 10);
    if (ok) {
        await api.blog.postBlogEntry(event, title, text, isPublic);
        currentPage.value = 1;
        refreshKey.value += 1;
    }
}
</script>
