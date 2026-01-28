<template>
    <LayoutBase :title="t('UsersView.title')">
        <v-col>
            <v-row>
                <v-btn v-if="auth.canAdd(PermissionTarget.USER)" @click="createUser">
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("UsersView.newUser") }}
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
                    :items="users"
                    :items-length="totalItems"
                    :loading="loading"
                    :page="currentPage"
                    :search="search"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('UsersView.noUsersFound')"
                    :loading-text="t('UsersView.loadingUsers')"
                    @update:options="debouncedLoad"
                >
                    <template #item.date_joined="{ item }">
                        {{ d(item.date_joined, "long") }}
                    </template>
                    <template #item.actions="{ item }">
                        <v-btn
                            v-if="auth.canDelete(PermissionTarget.USER)"
                            density="compact"
                            variant="text"
                            color="red"
                            @click="deleteUser(item)"
                        >
                            <template #prepend>
                                <FontAwesomeIcon :icon="faXmark" />
                            </template>
                            Delete
                        </v-btn>
                        <v-btn
                            v-if="auth.canChange(PermissionTarget.USER)"
                            density="compact"
                            variant="text"
                            @click="editUser(item.id)"
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
    <UserDialog ref="dialog" />
</template>

<script setup lang="ts">
import { faPenToSquare, faPlus, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce } from "lodash-es";
import { type Ref, inject, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import { type VDataTable, type VDataTableServer } from "vuetify/components";

import * as api from "@/api";
import type { User } from "@/api";
import LayoutBase from "@/components/LayoutBase.vue";
import UserDialog from "@/components/UserDialog.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const { t, d } = useI18n();

const dialog: Ref<InstanceType<typeof UserDialog> | undefined> = ref(undefined);
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;

const toast = useToast();
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

function flushData() {
    refreshKey.value += 1;
}

async function load(args: LoadArgs) {
    loading.value = true;
    try {
        const response = await api.adminUsersList({ query: getLoadArgs(args) });
        users.value = response.data!.results;
        totalItems.value = response.data!.count;
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
            await api.adminUsersDestroy({ path: { id: item.id } });
            flushData();
            toast.success(t("UsersView.deleteSuccess"));
        } catch (e) {
            toast.error(t("UsersView.deleteFailure"));
            console.error(e);
        }
    }
}

async function editUser(id: number): Promise<void> {
    const response = await api.adminUsersRetrieve({ path: { id } });
    const ok = await dialog.value!.modal(response.data!);
    if (ok) {
        flushData();
    }
}

async function createUser() {
    const ok = await dialog.value!.modal();
    if (ok) {
        currentPage.value = 1;
        flushData();
    }
}
</script>
