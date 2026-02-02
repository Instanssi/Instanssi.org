<template>
    <span>
        <v-btn
            v-if="canDelete"
            density="compact"
            variant="text"
            color="red"
            @click="emit('delete')"
        >
            <template #prepend>
                <FontAwesomeIcon :icon="faXmark" />
            </template>
            {{ t("General.delete") }}
        </v-btn>
        <v-btn v-if="canEdit" density="compact" variant="text" @click="emit('edit')">
            <template #prepend>
                <FontAwesomeIcon :icon="faPenToSquare" />
            </template>
            {{ t("General.edit") }}
        </v-btn>
        <template v-if="auditLog && hasAuditLogPermission">
            <v-btn
                icon
                density="compact"
                variant="text"
                size="small"
                :title="t('AuditLogTable.title')"
                @click="auditLogDialogVisible = true"
            >
                <FontAwesomeIcon :icon="faClockRotateLeft" />
            </v-btn>
            <AuditLogDialog
                v-model="auditLogDialogVisible"
                :app-label="auditLog.appLabel"
                :model="auditLog.model"
                :object-pk="auditLog.objectPk"
            />
        </template>
    </span>
</template>

<script setup lang="ts">
import { faClockRotateLeft, faPenToSquare, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";

import AuditLogDialog from "@/components/auditlog/AuditLogDialog.vue";
import { PermissionTarget, useAuth } from "@/services/auth";

export interface AuditLogConfig {
    appLabel: string;
    model: string;
    objectPk: string | number;
}

const props = withDefaults(
    defineProps<{
        canEdit?: boolean;
        canDelete?: boolean;
        auditLog?: AuditLogConfig;
    }>(),
    {
        canEdit: true,
        canDelete: true,
        auditLog: undefined,
    }
);

const emit = defineEmits<{
    edit: [];
    delete: [];
}>();

const { t } = useI18n();
const auth = useAuth();

const auditLogDialogVisible = ref(false);
const hasAuditLogPermission = computed(
    () => props.auditLog && auth.canView(PermissionTarget.LOG_ENTRY)
);
</script>
