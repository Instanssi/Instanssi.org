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

        <v-dialog v-model="showDialog" max-width="600">
            <v-card>
                <v-card-title class="d-flex justify-space-between align-center">
                    <span>{{ title ?? t("LongTextCell.dialogTitle") }}</span>
                    <v-btn icon variant="text" density="compact" @click="showDialog = false">
                        <FontAwesomeIcon :icon="faXmark" />
                    </v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text class="pa-4" style="white-space: pre-wrap">{{ value }}</v-card-text>
            </v-card>
        </v-dialog>
    </div>
</template>

<script setup lang="ts">
import { faFileLines, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { ref } from "vue";
import { useI18n } from "vue-i18n";

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
