<template>
    <FontAwesomeIcon :icon="value ? faCheck : faXmark" :class="value ? trueClass : falseClass" />
</template>

<script setup lang="ts">
import { faCheck, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

withDefaults(
    defineProps<{
        value?: boolean;
        trueClass?: string;
        falseClass?: string;
    }>(),
    {
        value: false,
        trueClass: "text-green",
        falseClass: "text-red",
    }
);
</script>
