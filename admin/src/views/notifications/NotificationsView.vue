<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <v-card class="mb-4">
                <v-card-title>{{ t("NotificationsView.preferences.title") }}</v-card-title>
                <v-card-text>
                    <ToggleSwitch
                        v-model="notifyVoteCodeRequests"
                        :label-on="t('NotificationsView.preferences.voteCodeRequestsOn')"
                        :label-off="t('NotificationsView.preferences.voteCodeRequestsOff')"
                        :hint-on="t('NotificationsView.preferences.voteCodeRequestsHint')"
                        :hint-off="t('NotificationsView.preferences.voteCodeRequestsHint')"
                    />
                    <ToggleSwitch
                        v-model="notifyProgramEvents"
                        :label-on="t('NotificationsView.preferences.programEventsOn')"
                        :label-off="t('NotificationsView.preferences.programEventsOff')"
                        :hint-on="t('NotificationsView.preferences.programEventsHint')"
                        :hint-off="t('NotificationsView.preferences.programEventsHint')"
                    />
                    <ToggleSwitch
                        v-model="notifyCompoStarts"
                        :label-on="t('NotificationsView.preferences.compoStartsOn')"
                        :label-off="t('NotificationsView.preferences.compoStartsOff')"
                        :hint-on="t('NotificationsView.preferences.compoStartsHint')"
                        :hint-off="t('NotificationsView.preferences.compoStartsHint')"
                    />
                    <ToggleSwitch
                        v-model="notifyCompetitionStarts"
                        :label-on="t('NotificationsView.preferences.competitionStartsOn')"
                        :label-off="t('NotificationsView.preferences.competitionStartsOff')"
                        :hint-on="t('NotificationsView.preferences.competitionStartsHint')"
                        :hint-off="t('NotificationsView.preferences.competitionStartsHint')"
                    />
                </v-card-text>
                <v-card-actions class="justify-end">
                    <v-btn variant="elevated" color="primary" :loading="saving" @click="save">
                        <template #prepend>
                            <FontAwesomeIcon :icon="faSave" />
                        </template>
                        {{ t("General.save") }}
                    </v-btn>
                </v-card-actions>
            </v-card>
            <v-card>
                <v-card-title>{{ t("NotificationsView.push.title") }}</v-card-title>
                <v-card-text>
                    <v-alert
                        v-if="push.pushState.value === 'unsupported'"
                        type="warning"
                        variant="tonal"
                        class="mb-4"
                    >
                        {{ t("NotificationsView.push.unsupported") }}
                    </v-alert>
                    <v-alert
                        v-if="push.pushState.value === 'denied'"
                        type="error"
                        variant="tonal"
                        class="mb-4"
                    >
                        {{ t("NotificationsView.push.denied") }}
                    </v-alert>
                    <v-switch
                        :model-value="push.subscribed.value"
                        :label="t('NotificationsView.push.enable')"
                        :hint="t('NotificationsView.push.enableHint')"
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
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "vue-toastification";

import * as api from "@instanssi/api";
import ToggleSwitch from "@/components/form/ToggleSwitch.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import { usePush } from "@/services/push";

const { t } = useI18n();
const toast = useToast();
const push = usePush();

const loading = ref(false);
const saving = ref(false);
const notifyVoteCodeRequests = ref(true);
const notifyProgramEvents = ref(true);
const notifyCompoStarts = ref(true);
const notifyCompetitionStarts = ref(true);

const breadcrumbs = computed<BreadcrumbItem[]>(() => [{ title: t("NotificationsView.title") }]);

async function save(): Promise<void> {
    saving.value = true;
    try {
        await api.userInfoPartialUpdate({
            body: {
                notify_vote_code_requests: notifyVoteCodeRequests.value,
                notify_program_events: notifyProgramEvents.value,
                notify_compo_starts: notifyCompoStarts.value,
                notify_competition_starts: notifyCompetitionStarts.value,
            },
        });
        toast.success(t("NotificationsView.saveSuccess"));
    } catch (e) {
        toast.error(t("NotificationsView.saveFailure"));
        console.error(e);
    } finally {
        saving.value = false;
    }
}

async function onTogglePush(enabled: boolean | null): Promise<void> {
    if (enabled) {
        const ok = await push.subscribe();
        if (!ok) {
            toast.error(t("NotificationsView.push.subscribeFailure"));
        }
    } else {
        const ok = await push.unsubscribe();
        if (!ok) {
            toast.error(t("NotificationsView.push.unsubscribeFailure"));
        }
    }
}

async function loadPreferences(): Promise<void> {
    try {
        const result = await api.userInfoRetrieve();
        const data = result.data!;
        notifyVoteCodeRequests.value = data.notify_vote_code_requests ?? true;
        notifyProgramEvents.value = data.notify_program_events ?? true;
        notifyCompoStarts.value = data.notify_compo_starts ?? true;
        notifyCompetitionStarts.value = data.notify_competition_starts ?? true;
    } catch (e) {
        toast.error(t("NotificationsView.loadFailure"));
        console.error(e);
    }
}

onMounted(async () => {
    loading.value = true;
    await Promise.all([loadPreferences(), push.init()]);
    loading.value = false;
});
</script>
