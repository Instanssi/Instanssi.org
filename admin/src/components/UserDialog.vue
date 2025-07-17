<template>
    <BaseFormDialog
        ref="dialog"
        :title="t('UserDialog.title')"
        :ok-text="t('General.save')"
        ok-icon="fas fa-floppy-disk"
        :width="1000"
        :loading="loading"
        @submit="submit"
    >
        <v-form>
            <v-text-field
                v-model="username.value.value"
                :error-messages="username.errorMessage.value"
                variant="outlined"
                :readonly="!isNew"
                :label="t('UserDialog.labels.userName')"
            />
            <v-text-field
                v-if="!isNew"
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
import { computed, type Ref, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import { date as YupDate, object as yupObject, string as yupString } from "yup";

import * as api from "@/api";
import type { UserReadable } from "@/api";
import BaseFormDialog from "@/components/BaseFormDialog.vue";
import BaseDialog from "@/components/BaseInfoDialog.vue";
import { sleep } from "@/utils/sleep.ts";

const dialog: Ref<InstanceType<typeof BaseDialog> | undefined> = ref();

const { t } = useI18n();
const toast = useToast();
const existingId: Ref<number | undefined> = ref(0);
const loading = ref(false);

// Form validation
const validationSchema = yupObject({
    first_name: yupString().min(0).max(150),
    last_name: yupString().min(0).max(150),
    date_joined: YupDate(),
    username: yupString().required().min(1).max(150),
    email: yupString().email().required().min(1).max(254),
});
const { handleSubmit, setTouched, resetForm, setValues } = useForm({ validationSchema });
const first_name = useField<string>("first_name");
const last_name = useField<string>("last_name");
const date_joined = useField<string>("date_joined");
const username = useField<string>("username");
const email = useField<string>("email");
const isNew = computed(() => existingId.value === undefined);
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
        await api.usersCreate({
            body: {
                first_name: values.first_name,
                last_name: values.last_name,
                email: values.email,
                username: values.username,
            },
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
        await api.usersPartialUpdate({
            path: {
                id: itemId,
            },
            body: {
                first_name: values.first_name,
                last_name: values.last_name,
                email: values.email,
                username: values.username,
            },
        });
        toast.success(t("UserDialog.editSuccess"));
        return true;
    } catch (e) {
        toast.error(t("UserDialog.editFailure"));
        console.error(e);
    }
    return false;
}

async function modal(item: UserReadable | undefined = undefined) {
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
