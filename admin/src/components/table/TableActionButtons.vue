<template>
    <span>
        <v-btn
            v-if="canView"
            class="ml-1 mr-1"
            icon
            density="compact"
            variant="elevated"
            size="small"
            color="blue"
            :title="t('General.view')"
            @click="emit('view')"
        >
            <FontAwesomeIcon :icon="faEye" />
        </v-btn>
        <v-btn
            v-if="canDelete"
            class="ml-1 mr-1"
            icon
            density="compact"
            variant="elevated"
            size="small"
            color="red"
            :title="t('General.delete')"
            @click="emit('delete')"
        >
            <FontAwesomeIcon :icon="faXmark" />
        </v-btn>
        <v-btn
            v-if="canEdit"
            class="ml-1 mr-1"
            icon
            density="compact"
            variant="elevated"
            color="green"
            size="small"
            :title="t('General.edit')"
            @click="emit('edit')"
        >
            <FontAwesomeIcon :icon="faPenToSquare" />
        </v-btn>
        <template v-if="auditLog && hasAuditLogPermission">
            <v-btn
                icon
                class="ml-1 mr-1"
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
import {
    faClockRotateLeft,
    faEye,
    faPenToSquare,
    faXmark,
} from "@fortawesome/free-solid-svg-icons";
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
        canView?: boolean;
        canEdit?: boolean;
        canDelete?: boolean;
        auditLog?: AuditLogConfig;
    }>(),
    {
        canView: false,
        canEdit: true,
        canDelete: true,
        auditLog: undefined,
    }
);

const emit = defineEmits<{
    view: [];
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
