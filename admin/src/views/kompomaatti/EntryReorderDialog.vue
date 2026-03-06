<template>
    <BaseDialog ref="dialog" :title="t('EntryReorderDialog.title')" :width="600">
        <v-card-text v-if="!compoId" class="text-center pa-6">
            {{ t("EntryReorderDialog.selectCompo") }}
        </v-card-text>
        <template v-else>
            <v-card-text v-if="loading" class="text-center pa-6">
                <v-progress-circular indeterminate />
            </v-card-text>
            <v-card-text v-else-if="orderedEntries.length === 0" class="text-center pa-6">
                {{ t("EntryReorderDialog.noEntries") }}
            </v-card-text>
            <v-card-text v-else class="pa-2">
                <div ref="dragListRef">
                    <div
                        v-for="(element, index) in orderedEntries"
                        :key="element.id"
                        :data-value="element.id"
                    >
                        <v-card variant="outlined" class="mb-1 drag-item" density="compact">
                            <v-card-text class="d-flex align-center pa-2" style="cursor: grab">
                                <span class="text-medium-emphasis mr-3">{{ index + 1 }}.</span>
                                <img
                                    v-if="element.imagefile_thumbnail_url"
                                    :src="element.imagefile_thumbnail_url"
                                    class="mr-3"
                                    style="
                                        width: 40px;
                                        height: 25px;
                                        object-fit: cover;
                                        border-radius: 2px;
                                    "
                                />
                                <div>
                                    <strong>{{ element.name }}</strong>
                                    <span class="text-medium-emphasis ml-2">{{
                                        element.creator
                                    }}</span>
                                </div>
                            </v-card-text>
                        </v-card>
                    </div>
                </div>
            </v-card-text>
            <v-divider />
            <v-card-actions>
                <v-spacer />
                <v-btn variant="text" @click="close">
                    {{ t("EntryReorderDialog.cancel") }}
                </v-btn>
                <v-btn
                    variant="elevated"
                    color="primary"
                    :loading="saving"
                    :disabled="orderedEntries.length === 0"
                    @click="save"
                >
                    {{ t("EntryReorderDialog.save") }}
                </v-btn>
            </v-card-actions>
        </template>
    </BaseDialog>
</template>

<script setup lang="ts">
import { dragAndDrop } from "@formkit/drag-and-drop/vue";
import { type Ref, ref, watch, nextTick } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import * as api from "@/api";
import type { CompoEntry } from "@/api";
import BaseDialog from "@/components/dialogs/BaseDialog.vue";
import { getApiErrorMessage } from "@/utils/http";

interface Props {
    eventId: number;
    compoId: number | null;
}

const props = defineProps<Props>();
const emit = defineEmits<{ saved: [] }>();
const { t } = useI18n();
const toast = useToast();

const dialog: Ref<InstanceType<typeof BaseDialog> | undefined> = ref(undefined);
const dragListRef: Ref<HTMLElement | undefined> = ref(undefined);
const orderedEntries: Ref<CompoEntry[]> = ref([]);
const loading = ref(false);
const saving = ref(false);

defineExpose({ open });

function open() {
    dialog.value?.modal();
    if (props.compoId) {
        loadEntries();
    }
}

function close() {
    dialog.value?.setResult(false);
}

watch(
    () => props.compoId,
    (newVal) => {
        if (newVal) {
            loadEntries();
        } else {
            orderedEntries.value = [];
        }
    }
);

async function loadEntries() {
    if (!props.compoId) return;
    loading.value = true;
    try {
        const response = await api.adminEventKompomaattiEntriesList({
            path: { event_pk: props.eventId },
            query: {
                compo: props.compoId,
                ordering: "order_index",
                limit: 1000,
            },
        });
        orderedEntries.value = response.data!.results;
        await nextTick();
        dragAndDrop<CompoEntry>({
            parent: dragListRef,
            values: orderedEntries,
        });
    } catch (e) {
        toast.error(getApiErrorMessage(e, t("EntryReorderDialog.loadFailure")));
        console.error(e);
    } finally {
        loading.value = false;
    }
}

async function save() {
    if (!props.compoId) return;
    saving.value = true;
    try {
        await api.adminEventKompomaattiEntriesReorderCreate({
            path: { event_pk: props.eventId },
            body: {
                compo: props.compoId,
                entry_ids: orderedEntries.value.map((e) => e.id),
            },
        });
        toast.success(t("EntryReorderDialog.saveSuccess"));
        emit("saved");
        close();
    } catch (e) {
        toast.error(getApiErrorMessage(e, t("EntryReorderDialog.saveFailure")));
        console.error(e);
    } finally {
        saving.value = false;
    }
}
</script>

<style scoped>
.drag-item {
    transition: box-shadow 0.2s;
}

.drag-item:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
</style>
