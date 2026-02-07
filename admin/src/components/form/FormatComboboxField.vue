<template>
    <v-combobox
        v-model="formatsArray"
        :items="suggestions"
        :error-messages="errorMessage"
        variant="outlined"
        :label="label"
        multiple
        chips
        closable-chips
    />
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
    /** Pipe-separated format string (e.g. "png|jpg|gif") */
    modelValue: string;
    label: string;
    suggestions?: string[];
    errorMessage?: string;
}>();

const emit = defineEmits<{
    "update:modelValue": [value: string];
}>();

const formatsArray = computed({
    get: () => (props.modelValue ? props.modelValue.split("|").filter(Boolean) : []),
    set: (val: string[]) => {
        emit("update:modelValue", val.join("|"));
    },
});
</script>
