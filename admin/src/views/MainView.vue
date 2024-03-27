<template>
    <LayoutBase :title="t('MainView.title')"></LayoutBase>
</template>

<script setup lang="ts">
import LayoutBase from "@/components/LayoutBase.vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>
