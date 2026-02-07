<template>
    <div class="d-flex ga-2">
        <v-text-field
            v-model.number="displayValue"
            type="number"
            min="0"
            :error-messages="errorMessage"
            variant="outlined"
            :label="label"
            class="flex-grow-1"
        />
        <v-select
            v-model="sizeUnit"
            :items="sizeUnitOptions"
            variant="outlined"
            style="max-width: 100px"
        />
    </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

type SizeUnit = "B" | "KB" | "MB" | "GB";

const sizeUnitOptions: SizeUnit[] = ["B", "KB", "MB", "GB"];

const sizeMultipliers: Record<SizeUnit, number> = {
    B: 1,
    KB: 1024,
    MB: 1024 * 1024,
    GB: 1024 * 1024 * 1024,
};

const props = defineProps<{
    /** Value in bytes (null means no limit) */
    modelValue: number | null;
    label: string;
    errorMessage?: string;
}>();

const emit = defineEmits<{
    "update:modelValue": [value: number | null];
}>();

const sizeUnit = ref<SizeUnit>(bestUnitForBytes(props.modelValue));

/** Convert bytes to display value based on unit */
function bytesToUnit(bytes: number | null, unit: SizeUnit): number | null {
    if (bytes === null || bytes === undefined) return null;
    return Math.round((bytes / sizeMultipliers[unit]) * 100) / 100;
}

/** Convert display value to bytes based on unit */
function unitToBytes(value: number | null, unit: SizeUnit): number | null {
    if (value === null || value === undefined) return null;
    return Math.round(value * sizeMultipliers[unit]);
}

/** Determine best unit for a byte value */
function bestUnitForBytes(bytes: number | null): SizeUnit {
    if (bytes === null || bytes === undefined || bytes === 0) return "MB";
    if (bytes >= sizeMultipliers.GB) return "GB";
    if (bytes >= sizeMultipliers.MB) return "MB";
    if (bytes >= sizeMultipliers.KB) return "KB";
    return "B";
}

const displayValue = computed({
    get: () => bytesToUnit(props.modelValue, sizeUnit.value),
    set: (val) => {
        emit("update:modelValue", unitToBytes(val, sizeUnit.value));
    },
});

// When external modelValue changes significantly (e.g. on load), pick the best unit
watch(
    () => props.modelValue,
    (newVal, oldVal) => {
        if (oldVal === null && newVal !== null) {
            sizeUnit.value = bestUnitForBytes(newVal);
        }
    }
);
</script>
