<template>
    <v-row align="center">
        <v-col cols="12" :md="modelValue ? 4 : 12">
            <v-switch
                :model-value="modelValue"
                :error-messages="errorMessage"
                :label="switchLabel"
                color="error"
                hide-details="auto"
                :class="{ 'text-red-darken-3': modelValue }"
                @update:model-value="$emit('update:modelValue', $event ?? false)"
            />
        </v-col>
        <v-col v-if="modelValue" cols="12" md="8">
            <v-text-field
                :model-value="reason"
                :error-messages="reasonErrorMessage"
                variant="outlined"
                :label="reasonLabel"
                hide-details="auto"
                @update:model-value="$emit('update:reason', $event)"
            />
        </v-col>
    </v-row>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps<{
    modelValue: boolean;
    reason: string;
    errorMessage?: string;
    reasonErrorMessage?: string;
    labelOn?: string;
    labelOff?: string;
    reasonLabel?: string;
}>();

defineEmits<{
    "update:modelValue": [value: boolean];
    "update:reason": [value: string];
}>();

const { t } = useI18n();

const switchLabel = computed(() =>
    props.modelValue
        ? (props.labelOn ?? t("General.disqualifiedOn"))
        : (props.labelOff ?? t("General.disqualifiedOff"))
);
</script>
