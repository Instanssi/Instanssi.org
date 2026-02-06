<template>
    <div v-if="value" class="long-text-cell">
        <v-btn
            icon
            variant="text"
            density="compact"
            size="small"
            :title="t('LongTextCell.clickToView')"
            @click="showDialog = true"
        >
            <FontAwesomeIcon :icon="faFileLines" />
        </v-btn>

        <ContentDialog v-model="showDialog" :title="title ?? t('LongTextCell.dialogTitle')">
            <div style="white-space: pre-wrap">{{ value }}</div>
        </ContentDialog>
    </div>
</template>

<script setup lang="ts">
import { faFileLines } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { ref } from "vue";
import { useI18n } from "vue-i18n";

import ContentDialog from "@/components/dialogs/ContentDialog.vue";

defineProps<{
    value: string | null | undefined;
    title?: string;
}>();

const { t } = useI18n();
const showDialog = ref(false);
</script>

<style scoped>
.long-text-cell {
    display: flex;
    align-items: center;
}
</style>
