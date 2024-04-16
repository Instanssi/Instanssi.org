<template>
    <BaseFormDialog
        :title="t('UserDialog.title')"
        :ok-text="t('General.save')"
        ok-icon="fas fa-floppy-disk"
        :width="1000"
        @submit="submit"
        ref="dialog"
    >
        <v-form>
            <v-text-field
                v-model="username.value.value"
                :error-messages="username.errorMessage.value"
                variant="outlined"
                readonly
                :label="t('UserDialog.labels.userName')"
            />
            <v-text-field
                v-model="date_joined.value.value"
                :error-messages="date_joined.errorMessage.value"
                variant="outlined"
                readonly
                :label="t('UserDialog.labels.dateJoined')"
            />
            <v-text-field
                v-model="email.value.value"
                :error-messages="email.errorMessage.value"
                variant="outlined"
                :label="t('UserDialog.labels.email')"
            />
            <v-text-field
                v-model="first_name.value.value"
                :error-messages="first_name.errorMessage.value"
                variant="outlined"
                :label="t('UserDialog.labels.firstName')"
            />
            <v-text-field
                v-model="last_name.value.value"
                :error-messages="last_name.errorMessage.value"
                variant="outlined"
                :label="t('UserDialog.labels.lastName')"
            />
        </v-form>
    </BaseFormDialog>
</template>

<script setup lang="ts">
import { type GenericObject, useField, useForm } from "vee-validate";
import { type Ref, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import { date as YupDate, object as yupObject, string as yupString } from "yup";

import type { User } from "@/api";
import BaseFormDialog from "@/components/BaseFormDialog.vue";
import BaseDialog from "@/components/BaseInfoDialog.vue";
import { useAPI } from "@/services/api";

const dialog: Ref<InstanceType<typeof BaseDialog> | undefined> = ref();

const { t } = useI18n();
const api = useAPI();
const toast = useToast();
const existingId: Ref<number | undefined> = ref(0);

// Form validation
const validationSchema = yupObject({
    first_name: yupString().min(0).max(150),
    last_name: yupString().min(0).max(150),
    date_joined: YupDate().required(),
    username: yupString().required().min(1).max(150),
    email: yupString().required().min(1).max(254),
});
const { handleSubmit, setTouched, resetForm, setValues } = useForm({ validationSchema });
const first_name = useField<string>("first_name");
const last_name = useField<string>("last_name");
const date_joined = useField<string>("date_joined");
const username = useField<string>("username");
const email = useField<string>("email");
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
        await api.users.usersCreate({
            first_name: values.first_name,
            last_name: values.last_name,
            email: values.email,
            username: values.username,
        });
        toast.success(t("UserDialog.createSuccess"));
        return true;
    } catch (e) {
        toast.error(t("UserDialog.createFailure"));
        console.error(e);
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        await api.users.usersPartialUpdate(itemId, {
            first_name: values.first_name,
            last_name: values.last_name,
            email: values.email,
            username: values.username,
        });
        toast.success(t("UserDialog.editSuccess"));
        return true;
    } catch (e) {
        toast.error(t("UserDialog.editFailure"));
        console.error(e);
    }
    return false;
}

async function modal(item: User | undefined = undefined) {
    if (item !== undefined) {
        existingId.value = item.id;
        setValues({
            first_name: item.first_name ?? "",
            last_name: item.last_name ?? "",
            email: item.email,
            date_joined: item.date_joined,
            username: item.username,
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
