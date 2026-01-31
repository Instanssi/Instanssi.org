<template>
    <LayoutBase :key="`competitions-${eventId}`" :breadcrumbs="breadcrumbs">
        <v-col>
            <v-row>
                <v-btn v-if="auth.canAdd(PermissionTarget.COMPETITION)" @click="createCompetition">
                    <template #prepend>
                        <FontAwesomeIcon :icon="faPlus" />
                    </template>
                    {{ t("CompetitionsView.newCompetition") }}
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
                    :key="`competitions-table-${refreshKey}`"
                    v-model:items-per-page="perPage"
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :headers="headers"
                    :items="competitions"
                    :items-length="totalItems"
                    :loading="loading"
                    :search="search"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('CompetitionsView.noCompetitionsFound')"
                    :loading-text="t('CompetitionsView.loadingCompetitions')"
                    @update:options="debouncedLoad"
                >
                    <template #item.active="{ item }">
                        <BooleanIcon :value="item.active" />
                    </template>
                    <template #item.participation_end="{ item }">
                        <DateTimeCell :value="item.participation_end" />
                    </template>
                    <template #item.start="{ item }">
                        <DateTimeCell :value="item.start" />
                    </template>
                    <template #item.end="{ item }">
                        <DateTimeCell :value="item.end" />
                    </template>
                    <template #item.actions="{ item }">
                        <TableActionButtons
                            :can-edit="auth.canChange(PermissionTarget.COMPETITION)"
                            :can-delete="auth.canDelete(PermissionTarget.COMPETITION)"
                            @edit="editCompetition(item.id)"
                            @delete="deleteCompetition(item)"
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
import { type Ref, computed, inject, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import type { VDataTableServer, VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { Competition } from "@/api";
import BooleanIcon from "@/components/table/BooleanIcon.vue";
import DateTimeCell from "@/components/table/DateTimeCell.vue";
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
    { title: t("CompetitionsView.title"), disabled: true },
]);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const competitions: Ref<Competition[]> = ref([]);
const search = ref("");
const refreshKey = ref(0);
const headers: ReadonlyHeaders = [
    {
        title: t("CompetitionsView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("CompetitionsView.headers.name"),
        sortable: true,
        key: "name",
    },
    {
        title: t("CompetitionsView.headers.participationEnd"),
        sortable: true,
        key: "participation_end",
    },
    {
        title: t("CompetitionsView.headers.start"),
        sortable: true,
        key: "start",
    },
    {
        title: t("CompetitionsView.headers.end"),
        sortable: true,
        key: "end",
    },
    {
        title: t("CompetitionsView.headers.active"),
        sortable: false,
        key: "active",
    },
    {
        title: t("CompetitionsView.headers.actions"),
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
        const response = await api.adminEventKompomaattiCompetitionsList({
            path: { event_pk: parseInt(props.eventId, 10) },
            query: {
                ...getLoadArgs(args),
            },
        });
        competitions.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("CompetitionsView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250);

async function deleteCompetition(item: Competition): Promise<void> {
    const text = t("CompetitionsView.confirmDelete", item);
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventKompomaattiCompetitionsDestroy({
                path: { event_pk: eventId.value, id: item.id },
            });
            toast.success(t("CompetitionsView.deleteSuccess"));
            flushData();
        } catch (e) {
            toast.error(t("CompetitionsView.deleteFailure"));
            console.error(e);
        }
    });
}

function editCompetition(id: number): void {
    router.push({ name: "competitions-edit", params: { eventId: eventId.value, id } });
}

function createCompetition(): void {
    router.push({ name: "competitions-new", params: { eventId: eventId.value } });
}
</script>
