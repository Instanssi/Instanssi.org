<template>
    <LayoutBase :title="t('UsersView.title')">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.USER)"
                    prepend-icon="fas fa-plus"
                    @click="createUser"
                >
                    {{ t("UsersView.newUser") }}
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
                    :items="users"
                    :items-length="totalItems"
                    :loading="loading"
                    :page="currentPage"
                    :search="search"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('UsersView.noUsersFound')"
                    :loading-text="t('UsersView.loadingUsers')"
                    v-model:items-per-page="perPage"
                    @update:options="debouncedLoad"
                >
                    <template v-slot:item.date_joined="{ item }">
                        {{ d(item.date_joined, "long") }}
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-btn
                            v-if="auth.canDelete(PermissionTarget.USER)"
                            density="compact"
                            variant="text"
                            @click="deleteUser(item)"
                            prepend-icon="fas fa-xmark"
                            color="red"
                            >Delete</v-btn
                        >
                        <v-btn
                            v-if="auth.canChange(PermissionTarget.USER)"
                            density="compact"
                            variant="text"
                            @click="editUser(item.id)"
                            prepend-icon="fas fa-pen-to-square"
                            >Edit</v-btn
                        >
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
    <UserDialog ref="dialog" />
</template>

<script setup lang="ts">
import { debounce } from "lodash-es";
import { type Ref, inject, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import type { VDataTableServer } from "vuetify/components";

import type { User } from "@/api";
import LayoutBase from "@/components/LayoutBase.vue";
import UserDialog from "@/components/UserDialog.vue";
import { useAPI } from "@/services/api";
import { PermissionTarget, useAuth } from "@/services/auth";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";

// Get vuetify data-table headers type, It is not currently exported, so just fetch it by hand :)
type ReadonlyHeaders = InstanceType<typeof VDataTableServer>["headers"];

const { t, d } = useI18n();

const dialog: Ref<InstanceType<typeof UserDialog> | undefined> = ref(undefined);
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;

const toast = useToast();
const api = useAPI();
const auth = useAuth();
const loading = ref(false);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const users: Ref<User[]> = ref([]);
const search = ref("");
const refreshKey = ref(0);
const headers: ReadonlyHeaders = [
    {
        title: t("UsersView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("UsersView.headers.userName"),
        sortable: false,
        key: "username",
    },
    {
        title: t("UsersView.headers.firstName"),
        sortable: true,
        key: "first_name",
    },
    {
        title: t("UsersView.headers.lastName"),
        sortable: true,
        key: "last_name",
    },
    {
        title: t("UsersView.headers.email"),
        sortable: true,
        key: "email",
    },
    {
        title: t("UsersView.headers.dateJoined"),
        sortable: false,
        key: "date_joined",
    },
    {
        title: t("UsersView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

async function load(args: LoadArgs) {
    loading.value = true;
    try {
        const { count, results } = await api.users.usersList(getLoadArgs(args));
        users.value = results;
        totalItems.value = count;
    } catch (e) {
        toast.error(t("UsersView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250); // Don't murderate the server API

async function deleteUser(item: User): Promise<void> {
    const text = t("UsersView.confirmDelete", item);
    const ok = await confirmDialog.value!.confirm(text);
    if (ok) {
        try {
            await api.users.usersDestroy({ id: item.id });
            toast.success(t("UsersView.deleteSuccess"));
        } catch (e) {
            toast.error(t("UsersView.deleteFailure"));
            console.error(e);
        }
        refreshKey.value += 1;
    }
}

async function editUser(id: number): Promise<void> {
    const item = await api.users.usersRetrieve({ id });
    if (await dialog.value!.modal(item)) {
        refreshKey.value += 1;
    }
}

async function createUser() {
    if (await dialog.value!.modal()) {
        currentPage.value = 1;
        refreshKey.value += 1;
    }
}
</script>
