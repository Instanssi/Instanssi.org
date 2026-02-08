<template>
    <v-switch
        :model-value="modelValue"
        :error-messages="errorMessage"
        :disabled="disabled"
        :label="currentLabel"
        :hint="currentHint"
        :persistent-hint="!!currentHint"
        :hide-details="!currentHint ? 'auto' : false"
        :color="color"
        :class="[className, { [activeClass]: modelValue && activeClass }]"
        @update:model-value="$emit('update:modelValue', $event ?? false)"
    />
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
    defineProps<{
        modelValue: boolean;
        errorMessage?: string;
        disabled?: boolean;
        labelOn: string;
        labelOff: string;
        hintOn?: string;
        hintOff?: string;
        color?: string;
        activeClass?: string;
        className?: string;
    }>(),
    {
        errorMessage: undefined,
        disabled: false,
        hintOn: undefined,
        hintOff: undefined,
        color: undefined,
        activeClass: "text-green-darken-3",
        className: "mb-4",
    }
);

defineEmits<{
    "update:modelValue": [value: boolean];
}>();

const currentLabel = computed(() => (props.modelValue ? props.labelOn : props.labelOff));

const currentHint = computed(() => {
    if (props.modelValue) {
        return props.hintOn;
    }
    return props.hintOff;
});
</script>
