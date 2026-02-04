<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <v-card>
                <v-card-text>
                    <v-form @submit.prevent="submit">
                        <v-row>
                            <v-col cols="12" md="6">
                                <v-select
                                    v-model.number="competition.value.value"
                                    :items="competitionOptions"
                                    :error-messages="competition.errorMessage.value"
                                    variant="outlined"
                                    :label="
                                        t('CompetitionParticipationEditView.labels.competition') +
                                        ' *'
                                    "
                                    :disabled="isEditMode"
                                />
                            </v-col>
                            <v-col cols="12" md="6">
                                <v-autocomplete
                                    v-model.number="user.value.value"
                                    :items="userOptions"
                                    :error-messages="user.errorMessage.value"
                                    variant="outlined"
                                    :label="
                                        t('CompetitionParticipationEditView.labels.user') + ' *'
                                    "
                                    :disabled="isEditMode"
                                />
                            </v-col>
                        </v-row>

                        <v-text-field
                            v-model="participantName.value.value"
                            :error-messages="participantName.errorMessage.value"
                            variant="outlined"
                            :label="t('CompetitionParticipationEditView.labels.participantName')"
                        />

                        <FormSection>
                            {{ t("CompetitionParticipationEditView.sections.scoring") }}
                        </FormSection>
                        <v-row>
                            <v-col cols="12" md="6">
                                <v-text-field
                                    v-model.number="score.value.value"
                                    type="number"
                                    :error-messages="score.errorMessage.value"
                                    variant="outlined"
                                    :label="t('CompetitionParticipationEditView.labels.score')"
                                />
                            </v-col>
                            <v-col v-if="isEditMode" cols="12" md="6">
                                <v-text-field
                                    :model-value="rankDisplay"
                                    variant="outlined"
                                    :label="t('CompetitionParticipationEditView.labels.rank')"
                                    readonly
                                />
                            </v-col>
                        </v-row>

                        <FormSection>
                            {{ t("CompetitionParticipationEditView.sections.disqualification") }}
                        </FormSection>
                        <DisqualificationField
                            v-model="disqualified.value.value"
                            v-model:reason="disqualifiedReason.value.value"
                            :error-message="disqualified.errorMessage.value"
                            :reason-error-message="disqualifiedReason.errorMessage.value"
                            :label-on="t('CompetitionParticipationEditView.labels.disqualifiedOn')"
                            :label-off="
                                t('CompetitionParticipationEditView.labels.disqualifiedOff')
                            "
                            :reason-label="
                                t('CompetitionParticipationEditView.labels.disqualifiedReason')
                            "
                        />
                    </v-form>
                </v-card-text>
                <v-card-actions class="justify-end">
                    <AuditLogButton
                        v-if="isEditMode"
                        app-label="kompomaatti"
                        model="competitionparticipation"
                        :object-pk="props.id"
                    />
                    <v-spacer />
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
import { computed, onMounted, ref, type Ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import {
    boolean as yupBoolean,
    number as yupNumber,
    object as yupObject,
    string as yupString,
} from "yup";

import * as api from "@/api";
import type { Competition, User } from "@/api";
import AuditLogButton from "@/components/auditlog/AuditLogButton.vue";
import DisqualificationField from "@/components/form/DisqualificationField.vue";
import FormSection from "@/components/form/FormSection.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { useEvents } from "@/services/events";
import { handleApiError, type FieldMapping } from "@/utils/http";

/** Maps API field names (snake_case) to form field names (camelCase) */
const API_FIELD_MAPPING: FieldMapping = {
    competition: "competition",
    user: "user",
    participant_name: "participantName",
    score: "score",
    disqualified: "disqualified",
    disqualified_reason: "disqualifiedReason",
};

const props = defineProps<{
    eventId: string;
    id?: string;
}>();

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const toast = useToast();
const { getEventById } = useEvents();

const loading = ref(false);
const saving = ref(false);
const participationName = ref<string>("");
const eventId = computed(() => parseInt(props.eventId, 10));
const isEditMode = computed(() => props.id !== undefined);

const competitions: Ref<Competition[]> = ref([]);
const users: Ref<User[]> = ref([]);
const rankDisplay = ref<string>("-");

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = [
        {
            title: getEventById(eventId.value)?.name ?? "...",
            to: { name: "dashboard", params: { eventId: props.eventId } },
        },
        {
            title: t("CompetitionParticipationsView.title"),
            to: { name: "competition-participations", params: { eventId: props.eventId } },
        },
    ];
    if (isEditMode.value) {
        items.push({ title: participationName.value || "...", disabled: true });
    } else {
        items.push({ title: t("Breadcrumbs.newParticipation"), disabled: true });
    }
    return items;
});

const competitionOptions = computed(() =>
    competitions.value.map((c) => ({ title: c.name, value: c.id }))
);
const userOptions = computed(() => users.value.map((u) => ({ title: u.username, value: u.id })));

// Form validation
const validationSchema = yupObject({
    competition: yupNumber().required(),
    user: yupNumber().required(),
    participantName: yupString().max(64),
    score: yupNumber().nullable(),
    disqualified: yupBoolean(),
    disqualifiedReason: yupString(),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        competition: null as number | null,
        user: null as number | null,
        participantName: "",
        score: null as number | null,
        disqualified: false,
        disqualifiedReason: "",
    },
});

const competition = useField<number | null>("competition");
const user = useField<number | null>("user");
const participantName = useField<string>("participantName");
const score = useField<number | null>("score");
const disqualified = useField<boolean>("disqualified");
const disqualifiedReason = useField<string>("disqualifiedReason");

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

function buildBody(values: GenericObject, isCreate: boolean) {
    return {
        // competition and user can only be set on create, not on edit
        competition: isCreate ? values.competition : undefined,
        user: isCreate ? values.user : undefined,
        participant_name: values.participantName || "",
        score: values.score,
        disqualified: values.disqualified,
        disqualified_reason: values.disqualifiedReason || "",
    };
}

async function createItem(values: GenericObject) {
    try {
        await api.adminEventKompomaattiCompetitionParticipationsCreate({
            path: { event_pk: eventId.value },
            body: buildBody(values, true),
        });
        toast.success(t("CompetitionParticipationEditView.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(
            e,
            setErrors,
            toast,
            t("CompetitionParticipationEditView.createFailure"),
            API_FIELD_MAPPING
        );
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        await api.adminEventKompomaattiCompetitionParticipationsPartialUpdate({
            path: { event_pk: eventId.value, id: itemId },
            body: buildBody(values, false),
        });
        toast.success(t("CompetitionParticipationEditView.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(
            e,
            setErrors,
            toast,
            t("CompetitionParticipationEditView.editFailure"),
            API_FIELD_MAPPING
        );
    }
    return false;
}

function goBack() {
    router.push({
        name: "competition-participations",
        params: { eventId: props.eventId },
        query: route.query,
    });
}

async function loadCompetitions() {
    try {
        const response = await api.adminEventKompomaattiCompetitionsList({
            path: { event_pk: eventId.value },
            query: { limit: 100 },
        });
        competitions.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load competitions:", e);
    }
}

async function loadUsers() {
    try {
        const response = await api.adminUsersList({
            query: { limit: 1000 },
        });
        users.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load users:", e);
    }
}

onMounted(async () => {
    await Promise.all([loadCompetitions(), loadUsers()]);

    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminEventKompomaattiCompetitionParticipationsRetrieve({
                path: { event_pk: eventId.value, id: parseInt(props.id!, 10) },
            });
            const item = response.data!;
            participationName.value = item.participant_name || `#${item.id}`;
            rankDisplay.value = item.computed_rank?.toString() ?? "-";

            setValues({
                competition: item.competition,
                user: item.user,
                participantName: item.participant_name ?? "",
                score: item.score ?? null,
                disqualified: item.disqualified ?? false,
                disqualifiedReason: item.disqualified_reason ?? "",
            });
        } catch (e) {
            toast.error(t("CompetitionParticipationEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
