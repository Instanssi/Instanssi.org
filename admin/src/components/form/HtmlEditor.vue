<template>
    <div class="html-editor mb-4">
        <ckeditor
            :model-value="modelValue"
            :editor="ClassicEditor"
            :config="editorConfig"
            @ready="onReady"
        />
    </div>
</template>

<script setup lang="ts">
import { ClassicEditor, type Editor } from "ckeditor5";
import { Ckeditor } from "@ckeditor/ckeditor5-vue";

import "ckeditor5/ckeditor5.css";

import { editorConfig } from "@/ckeditor";

defineProps<{ modelValue?: string }>();
const emit = defineEmits<{ "update:modelValue": [value: string] }>();

function onReady(editor: Editor) {
    editor.model.document.on("change:data", () => {
        emit("update:modelValue", editor.getData());
    });
}
</script>

<style scoped>
.html-editor :deep(.ck-editor__editable) {
    min-height: 200px;
}
</style>
