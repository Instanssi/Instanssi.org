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

        <ContentDialog v-model="showDialog" :title="title ?? t('LongTextCell.dialogTitle')">
            <div v-if="sanitizedHtml" class="html-content" v-html="value"></div>
            <div v-else style="white-space: pre-wrap">{{ value }}</div>
        </ContentDialog>
    </div>
</template>

<script setup lang="ts">
import { faFileLines } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { ref } from "vue";
import { useI18n } from "vue-i18n";

import ContentDialog from "@/components/dialogs/ContentDialog.vue";

defineProps<{
    value: string | null | undefined;
    title?: string;
    sanitizedHtml?: boolean;
}>();

const { t } = useI18n();
const showDialog = ref(false);
</script>

<style scoped>
.long-text-cell {
    display: flex;
    align-items: center;
}

.html-content :deep(h1),
.html-content :deep(h2),
.html-content :deep(h3),
.html-content :deep(h4),
.html-content :deep(h5),
.html-content :deep(h6) {
    margin-top: 1em;
    margin-bottom: 0.5em;
    font-weight: 600;
    line-height: 1.3;
}

.html-content :deep(h1) {
    font-size: 1.6em;
}

.html-content :deep(h2) {
    font-size: 1.4em;
}

.html-content :deep(h3) {
    font-size: 1.2em;
}

.html-content :deep(h4) {
    font-size: 1.1em;
}

.html-content :deep(p) {
    margin-bottom: 0.75em;
}

.html-content :deep(ul),
.html-content :deep(ol) {
    margin-bottom: 0.75em;
    padding-left: 1.5em;
}

.html-content :deep(li) {
    margin-bottom: 0.25em;
}

.html-content :deep(blockquote) {
    border-left: 3px solid rgba(var(--v-border-color), var(--v-border-opacity));
    padding-left: 1em;
    margin: 0.75em 0;
    color: rgba(var(--v-theme-on-surface), 0.6);
}

.html-content :deep(pre) {
    background: rgba(var(--v-theme-on-surface), 0.05);
    border-radius: 4px;
    padding: 0.75em 1em;
    margin-bottom: 0.75em;
    overflow-x: auto;
}

.html-content :deep(code) {
    font-family: "Fira Mono", monospace;
    font-size: 0.9em;
}

.html-content :deep(:not(pre) > code) {
    background: rgba(var(--v-theme-on-surface), 0.05);
    border-radius: 3px;
    padding: 0.15em 0.3em;
}

.html-content :deep(table) {
    border-collapse: collapse;
    margin-bottom: 0.75em;
    width: 100%;
}

.html-content :deep(th),
.html-content :deep(td) {
    border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    padding: 0.4em 0.75em;
    text-align: left;
}

.html-content :deep(th) {
    background: rgba(var(--v-theme-on-surface), 0.05);
    font-weight: 600;
}

.html-content :deep(hr) {
    border: none;
    border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    margin: 1em 0;
}

.html-content :deep(a) {
    color: rgb(var(--v-theme-primary));
    text-decoration: underline;
}

.html-content :deep(:first-child) {
    margin-top: 0;
}

.html-content :deep(:last-child) {
    margin-bottom: 0;
}
</style>
