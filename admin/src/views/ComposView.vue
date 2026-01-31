<template>
    <LayoutBase :key="`compos-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn v-if="auth.canAdd(PermissionTarget.COMPO)" @click="createCompo">
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("ComposView.newCompo") }}
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
                    :key="`compos-table-${refreshKey}`"
                    v-model:items-per-page="perPage"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="headers"
                    :items="compos"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="search"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('ComposView.noComposFound')"
                    :loading-text="t('ComposView.loadingCompos')"
                    @update:options="debouncedLoad"
                >
                    <template #item.active="{ item }">
                        <BooleanIcon :value="item.active" />
                    </template>
                    <template #item.adding_end="{ item }">
                        {{ d(item.adding_end, "long") }}
                    </template>
                    <template #item.voting_start="{ item }">
                        {{ d(item.voting_start, "long") }}
                    </template>
                    <template #item.voting_end="{ item }">
                        {{ d(item.voting_end, "long") }}
                    </template>
                    <template #item.actions="{ item }">
                        <v-btn
                            v-if="auth.canDelete(PermissionTarget.COMPO)"
                            density="compact"
                            variant="text"
                            color="red"
                            @click="deleteCompo(item)"
                        >
                            <template #prepend>
                                <FontAwesomeIcon :icon="faXmark" />
                            </template>
                            {{ t("General.delete") }}
                        </v-btn>
                        <v-btn
                            v-if="auth.canChange(PermissionTarget.COMPO)"
                            density="compact"
                            variant="text"
                            @click="editCompo(item.id)"
                        >
                            <template #prepend>
                                <FontAwesomeIcon :icon="faPenToSquare" />
                            </template>
                            {{ t("General.edit") }}
                        </v-btn>
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { faPenToSquare, faPlus, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce, parseInt } from "lodash-es";
import { type Ref, computed, inject, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTableServer, VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { Compo } from "@/api";
import BooleanIcon from "@/components/BooleanIcon.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/LayoutBase.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";

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
    { title: t("ComposView.title"), disabled: true },
]);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const compos: Ref<Compo[]> = ref([]);
const search = ref("");
const refreshKey = ref(0);
const headers: ReadonlyHeaders = [
    {
        title: t("ComposView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("ComposView.headers.name"),
        sortable: true,
        key: "name",
    },
    {
        title: t("ComposView.headers.addingEnd"),
        sortable: true,
        key: "adding_end",
    },
    {
        title: t("ComposView.headers.votingStart"),
        sortable: true,
        key: "voting_start",
    },
    {
        title: t("ComposView.headers.votingEnd"),
        sortable: true,
        key: "voting_end",
    },
    {
        title: t("ComposView.headers.active"),
        sortable: false,
        key: "active",
    },
    {
        title: t("ComposView.headers.actions"),
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
        const response = await api.adminEventKompomaattiComposList({
            path: { event_pk: parseInt(props.eventId, 10) },
            query: {
                ...getLoadArgs(args),
            },
        });
        compos.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("ComposView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

async function deleteCompo(item: Compo): Promise<void> {
    const text = t("ComposView.confirmDelete", item);
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventKompomaattiComposDestroy({
                path: { event_pk: eventId.value, id: item.id },
            });
            toast.success(t("ComposView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(t("ComposView.deleteFailure"));
            console.error(e);
        }
    });
}

function editCompo(id: number): void {
    router.push({ name: "compos-edit", params: { eventId: eventId.value, id } });
}

function createCompo(): void {
    router.push({ name: "compos-new", params: { eventId: eventId.value } });
}
</script>
