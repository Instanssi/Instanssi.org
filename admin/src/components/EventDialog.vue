<template>
    <BaseDialog
        :title="t('EventDialog.title')"
        :ok-text="t('General.save')"
        ok-icon="fas fa-floppy-disk"
        :width="1000"
        ref="dialog"
    >
        <v-form>
            <v-text-field v-model="name" variant="outlined" :label="t('EventDialog.labels.name')" />
            <v-text-field v-model="tag" variant="outlined" :label="t('EventDialog.labels.tag')" />
            <v-text-field
                type="date"
                v-model="date"
                variant="outlined"
                :label="t('EventDialog.labels.date')"
            />
            <v-text-field
                v-model="mainUrl"
                variant="outlined"
                :label="t('EventDialog.labels.mainUrl')"
            />
            <v-switch v-model="archived" :label="archivedLabel" />
        </v-form>
    </BaseDialog>
</template>

<script setup lang="ts">
import BaseDialog from "@/components/BaseDialog.vue";
import { computed, type Ref, ref } from "vue";
import { useI18n } from "vue-i18n";
import type { Event } from "@/api";

const dialog: Ref<InstanceType<typeof BaseDialog> | undefined> = ref();

const { t } = useI18n();
const name = ref("");
const tag = ref("");
const date = ref("");
const archived = ref(false);
const mainUrl = ref("");
const archivedLabel = computed(() =>
    archived.value ? t("EventDialog.labels.isArchived") : t("EventDialog.labels.isNotArchived")
);

async function modal(item: undefined | Event = undefined) {
    if (item !== undefined) {
        name.value = item.name;
        tag.value = item.tag ?? "";
        date.value = item.date;
        archived.value = item.archived ?? false;
        mainUrl.value = item.mainurl ?? "";
    } else {
        name.value = "";
        tag.value = "";
        date.value = "";
        archived.value = false;
        mainUrl.value = "";
    }
    const ok = (await dialog.value?.modal()) ?? false;
    return {
        ok,
        name: name.value,
        tag: tag.value,
        date: date.value,
        archived: archived.value,
        mainUrl: mainUrl.value,
    };
}

defineExpose({ modal });
</script>

<style scoped lang="scss"></style>
