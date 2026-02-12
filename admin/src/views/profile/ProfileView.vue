<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <InfoCard :title="t('ProfileView.sections.account')" class="mb-4">
                <InfoRow :label="t('ProfileView.labels.username')" :value="username" />
                <InfoRow :label="t('ProfileView.labels.email')" :value="email" />
                <InfoRow :label="t('ProfileView.labels.dateJoined')" :value="dateJoined" />
            </InfoCard>
            <v-card>
                <v-card-text>
                    <v-form @submit.prevent="submit">
                        <v-text-field
                            v-model="firstName.value.value"
                            :error-messages="firstName.errorMessage.value"
                            variant="outlined"
                            :label="t('ProfileView.labels.firstName')"
                        />
                        <v-text-field
                            v-model="lastName.value.value"
                            :error-messages="lastName.errorMessage.value"
                            variant="outlined"
                            :label="t('ProfileView.labels.lastName')"
                        />
                        <v-select
                            v-model="language.value.value"
                            :error-messages="language.errorMessage.value"
                            :label="t('ProfileView.labels.language')"
                            :items="languageOptions"
                            variant="outlined"
                        />
                    </v-form>
                </v-card-text>
                <v-card-actions class="justify-end">
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
import { useField, useForm } from "vee-validate";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";
import { object as yupObject, string as yupString } from "yup";

import * as api from "@/api";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import InfoCard from "@/components/table/InfoCard.vue";
import InfoRow from "@/components/table/InfoRow.vue";
import { LOCALE_NAMES, SUPPORTED_LOCALES, isSupportedLocale, type SupportedLocale } from "@/i18n";
import { useAuth } from "@/services/auth";
import { handleApiError, type FieldMapping } from "@/utils/http";

/** Maps API field names (snake_case) to form field names (camelCase) */
const API_FIELD_MAPPING: FieldMapping = {
    first_name: "firstName",
    last_name: "lastName",
    language: "language",
};

const { t, d } = useI18n();
const toast = useToast();
const authService = useAuth();

const loading = ref(false);
const saving = ref(false);
const username = ref("");
const email = ref("");
const dateJoined = ref("");

const breadcrumbs = computed<BreadcrumbItem[]>(() => [{ title: t("ProfileView.title") }]);

const languageOptions = SUPPORTED_LOCALES.map((loc) => ({
    title: LOCALE_NAMES[loc],
    value: loc,
}));

// Form validation
const validationSchema = yupObject({
    firstName: yupString().max(150),
    lastName: yupString().max(150),
    language: yupString()
        .required()
        .oneOf([...SUPPORTED_LOCALES]),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        firstName: "",
        lastName: "",
        language: "en",
    },
});

const firstName = useField<string>("firstName");
const lastName = useField<string>("lastName");
const language = useField<string>("language");

const submit = handleSubmit(async (values) => {
    saving.value = true;
    const ok = await saveProfile(values);
    saving.value = false;
    if (ok) {
        await authService.refreshStatus();
    }
});

interface ProfileFormValues {
    firstName: string;
    lastName: string;
    language: string;
}

async function saveProfile(values: ProfileFormValues): Promise<boolean> {
    try {
        await api.userInfoPartialUpdate({
            body: {
                first_name: values.firstName,
                last_name: values.lastName,
                language: values.language as SupportedLocale,
            },
        });
        toast.success(t("ProfileView.saveSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("ProfileView.saveFailure"), API_FIELD_MAPPING);
        return false;
    }
}

onMounted(async () => {
    loading.value = true;
    try {
        const result = await api.userInfoRetrieve();
        const data = result.data!;
        username.value = data.username;
        email.value = data.email;
        dateJoined.value = d(data.date_joined, "long");
        const lang = data.language;
        setValues({
            firstName: data.first_name ?? "",
            lastName: data.last_name ?? "",
            language: lang && isSupportedLocale(lang) ? lang : "en",
        });
    } catch (e) {
        toast.error(t("ProfileView.loadFailure"));
        console.error(e);
    } finally {
        loading.value = false;
    }
});
</script>
