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
    </span>
</template>

<script setup lang="ts">
import { faPenToSquare, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { useI18n } from "vue-i18n";

withDefaults(
    defineProps<{
        canEdit?: boolean;
        canDelete?: boolean;
    }>(),
    {
        canEdit: true,
        canDelete: true,
    }
);

const emit = defineEmits<{
    edit: [];
    delete: [];
}>();

const { t } = useI18n();
</script>
