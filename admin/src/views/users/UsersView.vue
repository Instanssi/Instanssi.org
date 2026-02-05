<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.USER)"
                    color="primary"
                    @click="createUser"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("UsersView.newUser") }}
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
                <v-select
                    v-model="filterIsActive"
                    :items="[
                        { title: t('UsersView.allStatuses'), value: null },
                        { title: t('UsersView.activeOnly'), value: true },
                        { title: t('UsersView.inactiveOnly'), value: false },
                    ]"
                    variant="outlined"
                    density="compact"
                    :label="t('UsersView.filterByStatus')"
                    style="max-width: 200px"
                    class="ma-0 pa-0 ml-4"
                />
                <v-select
                    v-model="filterIsStaff"
                    :items="[
                        { title: t('UsersView.allTypes'), value: null },
                        { title: t('UsersView.staffOnly'), value: true },
                        { title: t('UsersView.regularOnly'), value: false },
                    ]"
                    variant="outlined"
                    density="compact"
                    :label="t('UsersView.filterByType')"
                    style="max-width: 200px"
                    class="ma-0 pa-0 ml-4"
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
                    :items="users"
                    :items-length="totalItems"
                    :loading="loading"
                    :page="tableState.page.value"
                    :search="tableState.search.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('UsersView.noUsersFound')"
                    :loading-text="t('UsersView.loadingUsers')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.is_superuser="{ item }">
                        <BooleanIcon :value="item.is_superuser" />
                    </template>
                    <template #item.is_active="{ item }">
                        <BooleanIcon :value="item.is_active" />
                    </template>
                    <template #item.date_joined="{ item }">
                        <DateTimeCell :value="item.date_joined" />
                    </template>
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.USER)"
                            :can-delete="auth.canDelete(PermissionTarget.USER)"
                            @edit="editUser(item.id)"
                            @delete="deleteUser(item)"
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
import { debounce } from "lodash-es";
import { type Ref, inject, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { User } from "@/api";
import BooleanIcon from "@/components/table/BooleanIcon.vue";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import TableActionButtons from "@/components/table/TableActionButtons.vue";
import { useTableState } from "@/composables/useTableState";
import { PermissionTarget, useAuth } from "@/services/auth";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";
import { getApiErrorMessage } from "@/utils/http";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;
const toast = useToast();
const auth = useAuth();

const breadcrumbs: BreadcrumbItem[] = [{ title: t("UsersView.title"), disabled: true }];

const tableState = useTableState({
    filterKeys: ["is_active", "is_staff"],
    initialSort: { key: "username", order: "asc" },
});
const loading = ref(false);

const filterIsActive = tableState.useBooleanFilter("is_active");
const filterIsStaff = tableState.useBooleanFilter("is_staff");
const totalItems = ref(0);
const users: Ref<User[]> = ref([]);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);
const headers: ReadonlyHeaders = [
    {
        title: t("UsersView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("UsersView.headers.userName"),
        sortable: true,
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
        title: t("UsersView.headers.superuser"),
        sortable: false,
        key: "is_superuser",
    },
    {
        title: t("UsersView.headers.active"),
        sortable: false,
        key: "is_active",
    },
    {
        title: t("UsersView.headers.dateJoined"),
        sortable: true,
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
    if (lastLoadArgs.value) {
        load(lastLoadArgs.value);
    }
}

async function load(args: LoadArgs) {
    loading.value = true;
    lastLoadArgs.value = args;
    try {
        const response = await api.adminUsersList({
            query: {
                ...getLoadArgs(args),
                ...(filterIsActive.value !== null ? { is_active: filterIsActive.value } : {}),
                ...(filterIsStaff.value !== null ? { is_staff: filterIsStaff.value } : {}),
            },
        });
        users.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("UsersView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

// Reload when filters change
watch([filterIsActive, filterIsStaff], () => {
    if (lastLoadArgs.value) {
        debouncedLoad({ ...lastLoadArgs.value, page: 1 });
    }
});

const debouncedLoad = debounce(load, 250);

function onTableOptionsUpdate(args: LoadArgs) {
    tableState.onOptionsUpdate(args);
    debouncedLoad(args);
}

async function deleteUser(item: User): Promise<void> {
    const text = t("UsersView.confirmDelete", item);
    const ok = await confirmDialog.value!.confirm(text);
    if (ok) {
        try {
            await api.adminUsersDestroy({ path: { id: item.id } });
            flushData();
            toast.success(t("UsersView.deleteSuccess"));
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("UsersView.deleteFailure")));
            console.error(e);
        }
    }
}

function editUser(id: number): void {
    router.push({ name: "users-edit", params: { id }, query: route.query });
}

function createUser(): void {
    router.push({ name: "users-new", query: route.query });
}
</script>
