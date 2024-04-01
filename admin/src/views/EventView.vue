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
                    class="elevation-1 primary"
                    item-value="id"
                    density="compact"
                    :key="`blog-table-${refreshKey}`"
                    :headers="headers"
                    :items="events"
                    :items-length="totalItems"
                    :loading="loading"
                    :page="currentPage"
                    :items-per-page-options="pageSizeOptions"
                    :no-data-text="t('EventView.noEventsFound')"
                    :loading-text="t('EventView.loadingEvents')"
                    v-model:items-per-page="perPage"
                    @update:options="debouncedLoad"
                >
                    <template v-slot:item.archived="{ item }">
                        <v-icon v-if="item.archived" icon="fas fa-check" color="green" />
                        <v-icon v-else icon="fas fa-xmark" color="red" />
                    </template>
                    <template v-slot:item.date="{ item }">
                        {{ d(item.date, "long") }}
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-btn
                            v-if="auth.canDelete(PermissionTarget.EVENT)"
                            density="compact"
                            variant="text"
                            @click="deleteEvent(item)"
                            prepend-icon="fas fa-xmark"
                            color="red"
                            >Delete</v-btn
                        >
                        <v-btn
                            v-if="auth.canChange(PermissionTarget.EVENT)"
                            density="compact"
                            variant="text"
                            @click="editEvent(item.id)"
                            prepend-icon="fas fa-pen-to-square"
                            >Edit</v-btn
                        >
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
import type { VDataTableServer } from "vuetify/components";

import type { Event } from "@/api";
import EventDialog from "@/components/EventDialog.vue";
import LayoutBase from "@/components/LayoutBase.vue";
import { useAPI } from "@/services/api";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { type LoadArgs, getLoadArgs } from "@/services/utils/query_tools";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";

// Get vuetify data-table headers type, It is not currently exported, so just fetch it by hand :)
type ReadonlyHeaders = InstanceType<typeof VDataTableServer>["headers"];

const { t, d } = useI18n();

const dialog: Ref<InstanceType<typeof EventDialog> | undefined> = ref(undefined);
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;

const toast = useToast();
const eventService = useEvents();
const api = useAPI();
const auth = useAuth();
const loading = ref(false);
const pageSizeOptions = [25, 50, 100];
const perPage = ref(pageSizeOptions[0]);
const totalItems = ref(0);
const currentPage = ref(1);
const events: Ref<Event[]> = ref([]);
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

async function load(args: LoadArgs) {
    loading.value = true;
    const { offset, limit, sortBy } = getLoadArgs(args);
    try {
        const { count, results } = await api.events.eventsList(limit, undefined, offset, sortBy);
        events.value = results;
        totalItems.value = count;
    } catch (e) {
        toast.error(t("EventView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const debouncedLoad = debounce(load, 250); // Don't murderate the server API

async function deleteEvent(item: Event): Promise<void> {
    const text = t("EventView.confirmDelete", item);
    const ok = await confirmDialog.value!.confirm(text);
    if (ok) {
        try {
            await api.events.eventsDestroy(item.id);
            toast.success(t("EventView.deleteSuccess"));
        } catch (e) {
            toast.error(t("EventView.deleteFailure"));
            console.error(e);
        }
        refreshKey.value += 1;
        await eventService.refreshEvents();
    }
}

async function editEvent(id: number): Promise<void> {
    const item = await api.events.eventsRetrieve(id);
    if (await dialog.value!.modal(item)) {
        refreshKey.value += 1;
        await eventService.refreshEvents();
    }
}

async function createEvent() {
    if (await dialog.value!.modal()) {
        currentPage.value = 1;
        refreshKey.value += 1;
        await eventService.refreshEvents();
    }
}
</script>
