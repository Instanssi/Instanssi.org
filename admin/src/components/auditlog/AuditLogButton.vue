<template>
    <template v-if="hasPermission">
        <v-btn
            v-if="variant === 'button'"
            :color="color"
            :variant="buttonVariant"
            :size="size"
            @click="dialogVisible = true"
        >
            <template #prepend>
                <FontAwesomeIcon :icon="faClockRotateLeft" />
            </template>
            {{ t("AuditLogTable.title") }}
        </v-btn>
        <v-btn
            v-else
            :icon="true"
            :variant="buttonVariant"
            :size="size"
            :title="t('AuditLogTable.title')"
            @click="dialogVisible = true"
        >
            <FontAwesomeIcon :icon="faClockRotateLeft" />
        </v-btn>
        <AuditLogDialog
            v-model="dialogVisible"
            :app-label="props.appLabel"
            :model="props.model"
            :object-pk="props.objectPk"
        />
    </template>
</template>

<script setup lang="ts">
import { faClockRotateLeft } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";

import AuditLogDialog from "@/components/auditlog/AuditLogDialog.vue";
import { PermissionTarget, useAuth } from "@/services/auth";

const props = withDefaults(
    defineProps<{
        appLabel: string;
        model: string;
        objectPk?: string | number;

        variant?: "icon" | "button";
        color?: string;
        buttonVariant?: "text" | "flat" | "elevated" | "tonal" | "outlined" | "plain";
        size?: "x-small" | "small" | "default" | "large" | "x-large";
    }>(),
    {
        objectPk: undefined,

        variant: "button",
        color: "default",
        buttonVariant: "text",
        size: "default",
    }
);

const { t } = useI18n();
const auth = useAuth();

const hasPermission = computed(() => auth.canView(PermissionTarget.LOG_ENTRY));
const dialogVisible = ref(false);
</script>
