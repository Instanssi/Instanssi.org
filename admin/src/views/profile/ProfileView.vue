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
            <v-card class="mb-4">
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
                        <v-textarea
                            v-model="otherinfo.value.value"
                            :error-messages="otherinfo.errorMessage.value"
                            variant="outlined"
                            :label="t('ProfileView.labels.otherinfo')"
                            :hint="t('ProfileView.labels.otherinfoHint')"
                            persistent-hint
                            rows="3"
                        />
                        <v-select
                            v-model="language.value.value"
                            :error-messages="language.errorMessage.value"
                            :label="t('ProfileView.labels.language')"
                            :items="languageOptions"
                            variant="outlined"
                        />
                        <FormSection>
                            {{ t("ProfileView.notifications.preferencesTitle") }}
                        </FormSection>
                        <ToggleSwitch
                            v-model="notifyVoteCodeRequests"
                            :label-on="t('ProfileView.notifications.voteCodeRequestsOn')"
                            :label-off="t('ProfileView.notifications.voteCodeRequestsOff')"
                            :hint-on="t('ProfileView.notifications.voteCodeRequestsHint')"
                            :hint-off="t('ProfileView.notifications.voteCodeRequestsHint')"
                        />
                        <ToggleSwitch
                            v-model="notifyProgramEvents"
                            :label-on="t('ProfileView.notifications.programEventsOn')"
                            :label-off="t('ProfileView.notifications.programEventsOff')"
                            :hint-on="t('ProfileView.notifications.programEventsHint')"
                            :hint-off="t('ProfileView.notifications.programEventsHint')"
                        />
                        <ToggleSwitch
                            v-model="notifyCompoStarts"
                            :label-on="t('ProfileView.notifications.compoStartsOn')"
                            :label-off="t('ProfileView.notifications.compoStartsOff')"
                            :hint-on="t('ProfileView.notifications.compoStartsHint')"
                            :hint-off="t('ProfileView.notifications.compoStartsHint')"
                        />
                        <ToggleSwitch
                            v-model="notifyCompetitionStarts"
                            :label-on="t('ProfileView.notifications.competitionStartsOn')"
                            :label-off="t('ProfileView.notifications.competitionStartsOff')"
                            :hint-on="t('ProfileView.notifications.competitionStartsHint')"
                            :hint-off="t('ProfileView.notifications.competitionStartsHint')"
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
            <v-card>
                <v-card-title>{{ t("ProfileView.notifications.title") }}</v-card-title>
                <v-card-text>
                    <v-alert
                        v-if="push.pushState.value === 'unsupported'"
                        type="warning"
                        variant="tonal"
                        class="mb-4"
                    >
                        {{ t("ProfileView.notifications.unsupported") }}
                    </v-alert>
                    <v-alert
                        v-if="push.pushState.value === 'denied'"
                        type="error"
                        variant="tonal"
                        class="mb-4"
                    >
                        {{ t("ProfileView.notifications.denied") }}
                    </v-alert>
                    <v-switch
                        :model-value="push.subscribed.value"
                        :label="t('ProfileView.notifications.enable')"
                        :hint="t('ProfileView.notifications.enableHint')"
                        persistent-hint
                        :loading="push.loading.value"
                        :disabled="
                            push.pushState.value === 'unsupported' ||
                            push.pushState.value === 'denied'
                        "
                        color="primary"
                        @update:model-value="onTogglePush"
                    />
                </v-card-text>
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
import type { UserInfoWritable } from "@/api";
import FormSection from "@/components/form/FormSection.vue";
import ToggleSwitch from "@/components/form/ToggleSwitch.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import InfoCard from "@/components/table/InfoCard.vue";
import InfoRow from "@/components/table/InfoRow.vue";
import { LOCALE_NAMES, SUPPORTED_LOCALES } from "@/i18n";
import { useAuth } from "@/services/auth";
import { usePush } from "@/services/push";
import { handleApiError, type FieldMapping } from "@/utils/http";

/** Maps API field names (snake_case) to form field names (camelCase) */
const API_FIELD_MAPPING: FieldMapping = {
    first_name: "firstName",
    last_name: "lastName",
    otherinfo: "otherinfo",
    language: "language",
};

const { t, d } = useI18n();
const toast = useToast();
const authService = useAuth();
const push = usePush();

const loading = ref(false);
const saving = ref(false);
const username = ref("");
const email = ref("");
const dateJoined = ref("");
const notifyVoteCodeRequests = ref(true);
const notifyProgramEvents = ref(true);
const notifyCompoStarts = ref(true);
const notifyCompetitionStarts = ref(true);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [{ title: t("ProfileView.title") }]);

const languageOptions = [
    { title: t("ProfileView.labels.browserDefault"), value: "" },
    ...SUPPORTED_LOCALES.map((loc) => ({
        title: LOCALE_NAMES[loc],
        value: loc,
    })),
];

// Form validation
const validationSchema = yupObject({
    firstName: yupString().max(150),
    lastName: yupString().max(150),
    otherinfo: yupString().defined(),
    language: yupString()
        .defined()
        .oneOf(["", ...SUPPORTED_LOCALES]),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        firstName: "",
        lastName: "",
        otherinfo: "",
        language: "",
    },
});

const firstName = useField<string>("firstName");
const lastName = useField<string>("lastName");
const otherinfo = useField<string>("otherinfo");
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
    otherinfo: string;
    language: string;
}

async function saveProfile(values: ProfileFormValues): Promise<boolean> {
    try {
        await api.userInfoPartialUpdate({
            body: {
                first_name: values.firstName,
                last_name: values.lastName,
                otherinfo: values.otherinfo,
                language: values.language as UserInfoWritable["language"],
                notify_vote_code_requests: notifyVoteCodeRequests.value,
                notify_program_events: notifyProgramEvents.value,
                notify_compo_starts: notifyCompoStarts.value,
                notify_competition_starts: notifyCompetitionStarts.value,
            },
        });
        toast.success(t("ProfileView.saveSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("ProfileView.saveFailure"), API_FIELD_MAPPING);
        return false;
    }
}

async function onTogglePush(enabled: boolean | null): Promise<void> {
    if (enabled) {
        const ok = await push.subscribe();
        if (!ok) {
            toast.error(t("ProfileView.notifications.subscribeFailure"));
        }
    } else {
        const ok = await push.unsubscribe();
        if (!ok) {
            toast.error(t("ProfileView.notifications.unsubscribeFailure"));
        }
    }
}

async function loadProfile(): Promise<void> {
    try {
        const result = await api.userInfoRetrieve();
        const data = result.data!;
        username.value = data.username;
        email.value = data.email;
        dateJoined.value = d(data.date_joined, "long");
        setValues({
            firstName: data.first_name ?? "",
            lastName: data.last_name ?? "",
            otherinfo: data.otherinfo ?? "",
            language: data.language ?? "",
        });
        notifyVoteCodeRequests.value = data.notify_vote_code_requests ?? true;
        notifyProgramEvents.value = data.notify_program_events ?? true;
        notifyCompoStarts.value = data.notify_compo_starts ?? true;
        notifyCompetitionStarts.value = data.notify_competition_starts ?? true;
    } catch (e) {
        toast.error(t("ProfileView.loadFailure"));
        console.error(e);
    }
}

onMounted(async () => {
    loading.value = true;
    await Promise.all([loadProfile(), push.init()]);
    loading.value = false;
});
</script>
