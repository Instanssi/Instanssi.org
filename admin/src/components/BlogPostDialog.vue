<template>
    <BaseFormDialog
        ref="dialog"
        :title="t('BlogPostDialog.title')"
        :ok-text="t('General.save')"
        ok-icon="fas fa-floppy-disk"
        :width="1000"
        @submit="submit"
    >
        <v-text-field
            v-model="title.value.value"
            :error-messages="title.errorMessage.value"
            variant="outlined"
            :label="t('BlogPostDialog.labels.title')"
        />
        <VuetifyTiptap v-model="text.value.value" />
        <v-switch
            v-model="isPublic.value.value"
            :error-messages="isPublic.errorMessage.value"
            :label="switchLabel"
        />
    </BaseFormDialog>
</template>

<script setup lang="ts">
import { type GenericObject, useField, useForm } from "vee-validate";
import { type Ref, computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import { boolean as yupBoolean, object as yupObject, string as yupString } from "yup";

import type { BlogEntry } from "@/api";
import BaseFormDialog from "@/components/BaseFormDialog.vue";
import BaseDialog from "@/components/BaseInfoDialog.vue";
import { useAPI } from "@/services/api";

const dialog: Ref<InstanceType<typeof BaseDialog> | undefined> = ref();

const { t } = useI18n();
const api = useAPI();
const toast = useToast();
const existingId: Ref<number | undefined> = ref(undefined);
const eventId: Ref<number> = ref(0);
const switchLabel = computed(() =>
    isPublic.value.value
        ? t("BlogPostDialog.labels.postIsVisible")
        : t("BlogPostDialog.labels.postNotVisible")
);

// Form validation
const validationSchema = yupObject({
    title: yupString().required().min(1).max(128),
    text: yupString().required().min(1),
    isPublic: yupBoolean(),
});
const { handleSubmit, setTouched, resetForm, setValues } = useForm({ validationSchema });
const title = useField<string>("title");
const text = useField<string>("text");
const isPublic = useField<boolean>("isPublic");
const submit = handleSubmit(async (values) => {
    let ok: boolean;
    if (existingId.value !== undefined) {
        ok = await editItem(existingId.value, values);
    } else {
        ok = await createItem(values);
    }
    if (ok) {
        dialog.value?.setResult(true);
    }
});

async function createItem(values: GenericObject) {
    try {
        await api.blogEntries.blogEntriesCreate({
            requestBody: {
                event: eventId.value,
                title: values.title,
                text: values.text,
                public: values.isPublic,
            },
        });
        toast.success(t("BlogPostDialog.createSuccess"));
        return true;
    } catch (e) {
        toast.error(t("BlogPostDialog.createFailure"));
        console.error(e);
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        await api.blogEntries.blogEntriesPartialUpdate({
            id: itemId,
            requestBody: {
                title: values.title,
                text: values.text,
                public: values.isPublic,
            },
        });
        toast.success(t("BlogPostDialog.editSuccess"));
        return true;
    } catch (e) {
        toast.error(t("BlogPostDialog.editFailure"));
        console.error(e);
    }
    return false;
}

async function modal(event: number, item: BlogEntry | undefined = undefined) {
    eventId.value = event;
    if (item !== undefined) {
        existingId.value = item.id;
        setValues({
            title: item.title,
            isPublic: item.public ?? false,
            text: item.text,
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

<style scoped lang="scss"></style>
