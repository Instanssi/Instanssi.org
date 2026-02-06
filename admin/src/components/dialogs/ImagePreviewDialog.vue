<template>
    <ContentDialog
        v-model="visible"
        :title="t('PreviewDialog.imageTitle')"
        :max-width="900"
        content-class="pa-0"
    >
        <div class="d-flex justify-center">
            <v-img :src="src ?? undefined" max-height="70vh" max-width="100%" />
        </div>
    </ContentDialog>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import ContentDialog from "@/components/dialogs/ContentDialog.vue";

defineProps<{
    src: string | null | undefined;
}>();

const { t } = useI18n();
const visible = defineModel<boolean>({ default: false });
</script>
