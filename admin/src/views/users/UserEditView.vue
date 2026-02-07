<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <v-card>
                <v-card-text>
                    <v-form @submit.prevent="submit">
                        <v-text-field
                            v-model="username.value.value"
                            :error-messages="username.errorMessage.value"
                            variant="outlined"
                            :readonly="isEditMode"
                            :label="t('UserDialog.labels.userName') + ' *'"
                        />
                        <v-text-field
                            v-if="isEditMode"
                            v-model="dateJoined"
                            variant="outlined"
                            readonly
                            :label="t('UserDialog.labels.dateJoined')"
                        />
                        <v-text-field
                            v-model="email.value.value"
                            :error-messages="email.errorMessage.value"
                            variant="outlined"
                            :label="t('UserDialog.labels.email') + ' *'"
                        />
                        <v-text-field
                            v-model="firstName.value.value"
                            :error-messages="firstName.errorMessage.value"
                            variant="outlined"
                            :label="t('UserDialog.labels.firstName')"
                        />
                        <v-text-field
                            v-model="lastName.value.value"
                            :error-messages="lastName.errorMessage.value"
                            variant="outlined"
                            :label="t('UserDialog.labels.lastName')"
                        />
                        <v-switch
                            v-model="isActive.value.value"
                            :error-messages="isActive.errorMessage.value"
                            :label="isActiveLabel"
                        />
                        <v-switch
                            v-if="isEditMode"
                            v-model="isSystem"
                            readonly
                            disabled
                            :label="isSystemLabel"
                        />
                    </v-form>
                </v-card-text>
                <v-card-actions class="justify-end">
                    <v-btn variant="text" @click="goBack">
                        {{ t("General.cancel") }}
                    </v-btn>
                    <v-btn
                        variant="elevated"
                        color="primary"
                        :loading="saving"
                        :disabled="!meta.valid"
                        @click="submit"
                    >
                        <template #prepend>
                            <FontAwesomeIcon :icon="faSave" />
                        </template>
                        {{ t("General.save") }}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import { faFloppyDisk as faSave } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { parseInt } from "lodash-es";
import { type GenericObject, useField, useForm } from "vee-validate";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { boolean as yupBoolean, object as yupObject, string as yupString } from "yup";

import * as api from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { handleApiError, type FieldMapping } from "@/utils/http";

/** Maps API field names (snake_case) to form field names (camelCase) */
const API_FIELD_MAPPING: FieldMapping = {
    username: "username",
    email: "email",
    first_name: "firstName",
    last_name: "lastName",
    is_active: "isActive",
};

const props = defineProps<{
    id?: string;
}>();

const { t, d } = useI18n();
const route = useRoute();
const router = useRouter();
const toast = useToast();

const loading = ref(false);
const saving = ref(false);
const userName = ref<string>("");
const dateJoined = ref<string>("");
const isSystem = ref(false);
const isEditMode = computed(() => props.id !== undefined);

const isActiveLabel = computed(() =>
    isActive.value.value ? t("UserDialog.labels.isActive") : t("UserDialog.labels.isNotActive")
);
const isSystemLabel = computed(() =>
    isSystem.value ? t("UserDialog.labels.isSystem") : t("UserDialog.labels.isNotSystem")
);

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = [{ title: t("UsersView.title"), to: { name: "users" } }];
    if (isEditMode.value) {
        items.push({ title: userName.value || "...", disabled: true });
    } else {
        items.push({ title: t("UserEditView.newTitle"), disabled: true });
    }
    return items;
});

// Form validation
const validationSchema = yupObject({
    firstName: yupString().min(0).max(150),
    lastName: yupString().min(0).max(150),
    username: yupString().required().min(1).max(150),
    email: yupString().email().required().min(1).max(254),
    isActive: yupBoolean(),
});
const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        firstName: "",
        lastName: "",
        username: "",
        email: "",
        isActive: true,
    },
});
const firstName = useField<string>("firstName");
const lastName = useField<string>("lastName");
const username = useField<string>("username");
const email = useField<string>("email");
const isActive = useField<boolean>("isActive");

const submit = handleSubmit(async (values) => {
    saving.value = true;
    let ok: boolean;
    if (isEditMode.value) {
        ok = await editItem(parseInt(props.id!, 10), values);
    } else {
        ok = await createItem(values);
    }
    saving.value = false;
    if (ok) {
        goBack();
    }
});

function buildBody(values: GenericObject) {
    return {
        first_name: values.firstName,
        last_name: values.lastName,
        email: values.email,
        username: values.username,
        is_active: values.isActive,
    };
}

async function createItem(values: GenericObject) {
    try {
        await api.adminUsersCreate({
            body: buildBody(values),
        });
        toast.success(t("UserDialog.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("UserDialog.createFailure"), API_FIELD_MAPPING);
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        await api.adminUsersPartialUpdate({
            path: { id: itemId },
            body: buildBody(values),
        });
        toast.success(t("UserDialog.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("UserDialog.editFailure"), API_FIELD_MAPPING);
    }
    return false;
}

function goBack() {
    router.push({ name: "users", query: route.query });
}

onMounted(async () => {
    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminUsersRetrieve({
                path: { id: parseInt(props.id!, 10) },
            });
            const item = response.data!;
            userName.value = item.username;
            dateJoined.value = d(item.date_joined, "long");
            isSystem.value = item.is_system ?? false;
            setValues({
                firstName: item.first_name ?? "",
                lastName: item.last_name ?? "",
                email: item.email ?? "",
                username: item.username,
                isActive: item.is_active ?? true,
            });
        } catch (e) {
            toast.error(t("UserEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
