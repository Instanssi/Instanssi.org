<template>
    <LayoutBase :title="t('EventView.title')">
        <v-col>
            <v-row>
                <v-btn
                    v-if="auth.canAdd(PermissionTarget.EVENT)"
                    prepend-icon="fas fa-plus"
                    @click="createEvent"
                >
                    {{ t("EventView.newEvent") }}
                </v-btn>
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
                    :items="events"
                    :items-length="totalItems"
                    :loading="loading"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('EventView.noEventsFound')"
                    :loading-text="t('EventView.loadingEvents')"
                    @update:options="debouncedLoad"
                >
                    <template #item.archived="{ item }">
                        <v-icon v-if="item.archived" icon="fas fa-check" color="green" />
                        <v-icon v-else icon="fas fa-xmark" color="red" />
                    </template>
                    <template #item.date="{ item }">
                        {{ d(item.date, "long") }}
                    </template>
                    <template #item.actions="{ item }">
                        <v-btn
                            v-if="auth.canDelete(PermissionTarget.EVENT)"
                            density="compact"
                            variant="text"
                            prepend-icon="fas fa-xmark"
                            color="red"
                            @click="deleteEvent(item)"
                        >
                            Delete
                        </v-btn>
                        <v-btn
                            v-if="auth.canChange(PermissionTarget.EVENT)"
                            density="compact"
                            variant="text"
                            prepend-icon="fas fa-pen-to-square"
                            @click="editEvent(item.id)"
                        >
                            Edit
                        </v-btn>
                    </template>
                </v-data-table-server>
            </v-row>
        </v-col>
    </LayoutBase>
    <EventDialog ref="dialog" />
</template>

<script setup lang="ts">
import { debounce } from "lodash-es";
import { type Ref, inject, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import type { VDataTable } from "vuetify/components";

import * as api from "@/api";
import type { EventReadable } from "@/api";
import EventDialog from "@/components/EventDialog.vue";
import LayoutBase from "@/components/LayoutBase.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";

type ReadonlyHeaders = VDataTable["$props"]["headers"];

const { t, d } = useI18n();

const dialog: Ref<InstanceType<typeof EventDialog> | undefined> = ref(undefined);
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;

const toast = useToast();
const eventService = useEvents();
const auth = useAuth();
const loading = ref(false);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const events: Ref<EventReadable[]> = ref([]);
const refreshKey = ref(0);
const headers: ReadonlyHeaders = [
    {
        title: t("EventView.headers.id"),
        sortable: true,
        key: "id",
    },
    {
        title: t("EventView.headers.name"),
        sortable: false,
        key: "name",
    },
    {
        title: t("EventView.headers.tag"),
        sortable: false,
        key: "tag",
    },
    {
        title: t("EventView.headers.date"),
        sortable: true,
        key: "date",
    },
    {
        title: t("EventView.headers.archived"),
        sortable: false,
        key: "archived",
    },
    {
        title: t("EventView.headers.mainUrl"),
        sortable: false,
        key: "mainurl",
    },
    {
        title: t("EventView.headers.actions"),
        sortable: false,
        key: "actions",
        align: "end",
    },
];

async function flushData() {
    refreshKey.value += 1;
    await eventService.refreshEvents();
}

async function load(args: LoadArgs) {
    loading.value = true;
    try {
        const response = await api.eventsList({ query: getLoadArgs(args) });
        events.value = response.data!.results;
        totalItems.value = response.data!.count;
    } catch (e) {
        toast.error(t("EventView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250); // Don't murderate the server API

async function deleteEvent(item: EventReadable): Promise<void> {
    const text = t("EventView.confirmDelete", item);
    const ok = await confirmDialog.value!.confirm(text);
    if (ok) {
        try {
            await api.eventsDestroy({ path: { id: item.id } });
            await flushData();
            toast.success(t("EventView.deleteSuccess"));
        } catch (e) {
            toast.error(t("EventView.deleteFailure"));
            console.error(e);
        }
    }
}

async function editEvent(id: number): Promise<void> {
    const response = await api.eventsRetrieve({ path: { id } });
    const ok = await dialog.value!.modal(response.data!);
    if (ok) {
        await flushData();
    }
}

async function createEvent() {
    const ok = await dialog.value!.modal();
    if (ok) {
        currentPage.value = 1;
        await flushData();
    }
}
</script>
