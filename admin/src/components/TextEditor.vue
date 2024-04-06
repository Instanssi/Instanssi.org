<template>
    <v-input :error-messages="errorMessages" style="height: 400px;">
        <div class="d-flex flex-column text-editor fill-height">
            <v-toolbar
                density="compact"
            >
                <v-btn
                    icon="fas fa-bold"
                    size="x-small"
                />
                <v-btn
                    icon="fas fa-underline"
                    size="x-small"
                />
                <v-btn
                    icon="fas fa-italic"
                    size="x-small"
                />
                <v-btn
                    icon="fas fa-strikethrough"
                    size="x-small"
                />
            </v-toolbar>
            <EditorContent
                class="flex-grow-1"
                :editor="editor"
                v-model="model"
            />
        </div>
    </v-input>
</template>

<script setup lang="ts">
import { EditorContent, useEditor } from "@tiptap/vue-3";
import { StarterKit } from "@tiptap/starter-kit";

const model = defineModel<string>({ required: true, type: String });
const editor = useEditor({
    content: model.value,
    extensions: [
        StarterKit,
    ],
    onUpdate,
});

defineProps<{
    errorMessages: string[] | string | undefined,
}>();

function onUpdate() {
    model.value = editor.value?.getHTML() ?? "";
}

</script>

<style scoped lang="scss">
.text-editor {
    width: 100%;
    border: 1px solid black;
    border-radius: 4px;
    box-sizing: border-box;
}
</style>