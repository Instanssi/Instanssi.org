<template>
    <LayoutBase :title="t('MainView.title')" />
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import LayoutBase from "@/components/LayoutBase.vue";

const { t } = useI18n();
</script>
