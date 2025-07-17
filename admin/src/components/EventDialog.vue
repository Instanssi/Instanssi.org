<template>
    <BaseFormDialog
        ref="dialog"
        :title="t('EventDialog.title')"
        :ok-text="t('General.save')"
        ok-icon="fas fa-floppy-disk"
        :width="1000"
        :loading="loading"
        @submit="submit"
    >
        <v-form>
            <v-text-field
                v-model="name.value.value"
                :error-messages="name.errorMessage.value"
                variant="outlined"
                :label="t('EventDialog.labels.name')"
            />
            <v-text-field
                v-model="tag.value.value"
                :error-messages="tag.errorMessage.value"
                variant="outlined"
                :label="t('EventDialog.labels.tag')"
            />
            <v-text-field
                v-model="date.value.value"
                type="date"
                :error-messages="date.errorMessage.value"
                variant="outlined"
                :label="t('EventDialog.labels.date')"
            />
            <v-text-field
                v-model="mainUrl.value.value"
                :error-messages="mainUrl.errorMessage.value"
                variant="outlined"
                :label="t('EventDialog.labels.mainUrl')"
            />
            <v-switch
                v-model="archived.value.value"
                :error-messages="archived.errorMessage.value"
                :label="archivedLabel"
            />
        </v-form>
    </BaseFormDialog>
</template>

<script setup lang="ts">
import { type GenericObject, useField, useForm } from "vee-validate";
import { type Ref, computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import {
    date as YupDate,
    boolean as yupBoolean,
    object as yupObject,
    string as yupString,
} from "yup";

import * as api from "@/api";
import type { Event } from "@/api";
import BaseFormDialog from "@/components/BaseFormDialog.vue";
import BaseDialog from "@/components/BaseInfoDialog.vue";
import { sleep } from "@/utils/sleep.ts";

const dialog: Ref<InstanceType<typeof BaseDialog> | undefined> = ref();

const { t } = useI18n();
const toast = useToast();
const loading = ref(false);
const existingId: Ref<number | undefined> = ref(0);
const archivedLabel = computed(() =>
    archived.value ? t("EventDialog.labels.isArchived") : t("EventDialog.labels.isNotArchived")
);

// Form validation
const validationSchema = yupObject({
    name: yupString().required().min(1).max(64),
    tag: yupString().required().min(1).max(8),
    date: YupDate().required(),
    archived: yupBoolean(),
    mainUrl: yupString().required().url().max(200),
});
const { handleSubmit, setTouched, resetForm, setValues } = useForm({ validationSchema });
const name = useField<string>("name");
const tag = useField<string>("tag");
const date = useField<string>("date");
const archived = useField<boolean>("archived");
const mainUrl = useField<string>("mainUrl");
const submit = handleSubmit(async (values) => {
    let ok: boolean;
    loading.value = true;
    if (existingId.value !== undefined) {
        ok = await editItem(existingId.value, values);
    } else {
        ok = await createItem(values);
    }
    await sleep(250); // Add some mass to the operation
    loading.value = false;
    if (ok) {
        dialog.value?.setResult(true);
    }
});

async function createItem(values: GenericObject) {
    try {
        await api.eventsCreate({
            body: {
                name: values.name,
                date: values.date,
                archived: values.archived,
                tag: values.tag,
                mainurl: values.mainUrl,
            },
        });
        toast.success(t("EventDialog.createSuccess"));
        return true;
    } catch (e) {
        toast.error(t("EventDialog.createFailure"));
        console.error(e);
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        await api.eventsPartialUpdate({
            path: {
                id: itemId,
            },
            body: {
                name: values.name,
                date: values.date,
                archived: values.archived,
                tag: values.tag,
                mainurl: values.mainUrl,
            },
        });
        toast.success(t("EventDialog.editSuccess"));
        return true;
    } catch (e) {
        toast.error(t("EventDialog.editFailure"));
        console.error(e);
    }
    return false;
}

async function modal(item: Event | undefined = undefined) {
    if (item !== undefined) {
        existingId.value = item.id;
        setValues({
            name: item.name,
            tag: item.tag,
            date: item.date,
            archived: item.archived ?? false,
            mainUrl: item.mainurl ?? "",
        });
    } else {
        existingId.value = undefined;
        resetForm();
        setTouched(false);
    }
    return (await dialog.value?.modal()) ?? false;
}

defineExpose({ modal });
</script>
