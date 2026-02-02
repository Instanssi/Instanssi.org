<template>
    <div class="diff-viewer">
        <template v-if="Object.keys(changes).length > 0">
            <div v-for="(value, field) in changes" :key="field" class="diff-field mb-2">
                <span class="diff-field-name font-weight-medium">{{ field }}:</span>
                <div v-if="Array.isArray(value) && value.length === 2" class="diff-values">
                    <span class="diff-old text-error">{{ formatValue(value[0]) }}</span>
                    <span class="diff-arrow mx-1">→</span>
                    <span class="diff-new text-success">{{ formatValue(value[1]) }}</span>
                </div>
                <div v-else class="diff-value">
                    <span class="text-success">{{ formatValue(value) }}</span>
                </div>
            </div>
        </template>
        <span v-else class="text-grey">{{ t("AuditLogTable.noChanges") }}</span>
    </div>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

defineProps<{
    changes: Record<string, unknown>;
}>();

const { t } = useI18n();

function formatValue(value: unknown): string {
    if (value === null || value === undefined) {
        return "null";
    }
    if (typeof value === "boolean") {
        return value ? "true" : "false";
    }
    if (typeof value === "object") {
        return JSON.stringify(value);
    }
    const str = String(value);
    if (str.length > 100) {
        return str.substring(0, 100) + "...";
    }
    return str;
}
</script>

<style scoped>
.diff-viewer {
    font-size: 0.875rem;
}

.diff-field {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    align-items: baseline;
}

.diff-field-name {
    min-width: 100px;
}

.diff-values {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 0.25rem;
}

.diff-old {
    text-decoration: line-through;
}

.diff-arrow {
    color: #666;
}
</style>
