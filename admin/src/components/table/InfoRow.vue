<template>
    <tr>
        <td class="font-weight-bold">{{ label }}</td>
        <td>
            <slot>{{ value }}</slot>
        </td>
    </tr>
</template>

<script setup lang="ts">
defineProps<{
    label: string;
    value?: string | number | null;
}>();
</script>
