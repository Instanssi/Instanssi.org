<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.AUTH_TOKEN)"
                    color="primary"
                    class="mb-4"
                    @click="showCreateDialog = true"
                >
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("TokensView.newToken") }}
                </v-btn>
            </v-row>
        </v-col>
        <v-col>
            <v-row>
                <v-data-table-server
                    v-model:items-per-page="tableState.perPage.value"
                    :sort-by="tableState.sortByArray.value"
                    class="elevation-1 primary"
                    item-value="pk"
                    density="compact"
                    :headers="headers"
                    :items="tokens"
                    :items-length="totalItems"
                    :loading="loading"
                    :page="tableState.page.value"
                    :items-per-page-options="tableState.pageSizeOptions"
                    :no-data-text="t('TokensView.noTokensFound')"
                    :loading-text="t('TokensView.loadingTokens')"
                    @update:options="onTableOptionsUpdate"
                >
                    <template #item.token_key="{ item }">
                        <code>{{ item.token_key }}...</code>
                    </template>
                    <template #item.created="{ item }">
                        <DateTimeCell :value="item.created" />
                    </template>
                    <template #item.expiry="{ item }">
                        <DateTimeCell :value="item.expiry" />
                    </template>
                    <template #item.actions="{ item }">
                        <v-btn
                            v-if="auth.canDelete(PermissionTarget.AUTH_TOKEN)"
                            variant="text"
                            color="error"
                            size="small"
                            @click="deleteToken(item)"
                        >
                            <FontAwesomeIcon :icon="faTrash" />
                        </v-btn>
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>

        <TokenCreateDialog v-model:visible="showCreateDialog" @created="onTokenCreated" />

        <TokenCreatedDialog v-model:visible="showCreatedDialog" :token="createdToken" />
    </LayoutBase>
</template>

<script setup lang="ts">
import { faPlus, faTrash } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce } from "lodash-es";
import { type Ref, inject, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import { type VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { AuthToken } from "@/api";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import TokenCreateDialog from "@/views/tokens/TokenCreateDialog.vue";
import TokenCreatedDialog from "@/components/dialogs/TokenCreatedDialog.vue";
import { useTableState } from "@/composables/useTableState";
import { PermissionTarget, useAuth } from "@/services/auth";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";
import { getApiErrorMessage } from "@/utils/http";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const { t } = useI18n();
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;
const toast = useToast();
const auth = useAuth();

const breadcrumbs: BreadcrumbItem[] = [{ title: t("TokensView.title"), disabled: true }];

const loading = ref(false);
const tableState = useTableState({ initialSort: { key: "created", order: "desc" } });
const totalItems = ref(0);
const tokens: Ref<AuthToken[]> = ref([]);
const lastLoadArgs: Ref<LoadArgs | null> = ref(null);
const showCreateDialog = ref(false);
const showCreatedDialog = ref(false);
const createdToken = ref("");

const headers: ReadonlyHeaders = [
    {
        title: t("TokensView.headers.tokenKey"),
        sortable: false,
        key: "token_key",
    },
    {
        title: t("TokensView.headers.created"),
        sortable: true,
        key: "created",
    },
    {
        title: t("TokensView.headers.expiry"),
        sortable: true,
        key: "expiry",
    },
    {
        title: t("TokensView.headers.actions"),
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
        const response = await api.tokensList({ query: getLoadArgs(args) });
        tokens.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("TokensView.loadFailure"));
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

async function deleteToken(item: AuthToken): Promise<void> {
    const text = t("TokensView.confirmDelete", { tokenKey: item.token_key });
    const ok = await confirmDialog.value!.confirm(text);
    if (ok) {
        try {
            await api.tokensDestroy({ path: { digest: item.pk } });
            flushData();
            toast.success(t("TokensView.deleteSuccess"));
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("TokensView.deleteFailure")));
            console.error(e);
        }
    }
}

function onTokenCreated(token: string) {
    createdToken.value = token;
    showCreatedDialog.value = true;
    flushData();
}
</script>
