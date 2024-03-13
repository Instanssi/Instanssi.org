<template>
    <BaseDialog
        title="Blog post"
        ok-text="Save"
        ok-icon="fas fa-floppy-disk"
        :width="1000"
        ref="dialog"
    >
        <v-form>
            <v-text-field
                v-model="title"
                variant="outlined"
                label="Title"
            />
            <QuillEditor theme="snow" style="height: 300px" ref="editor" />
            <v-switch v-model="isPublic" :label="switchLabel" />
        </v-form>
    </BaseDialog>
</template>

<script setup lang="ts">
import BaseDialog from "@/components/BaseDialog.vue";
import { QuillEditor } from "@vueup/vue-quill";
import { computed, type Ref, ref } from "vue";

const dialog: Ref<InstanceType<typeof BaseDialog>|undefined> = ref(undefined);
const editor: Ref<InstanceType<typeof QuillEditor> | undefined> = ref(undefined);

const isPublic = ref(false);
const title = ref("");
const switchLabel = computed(() => isPublic.value
    ? "Post is visible for everyone"
    : "Post is private; only admins can see it"
)

async function modal() {
    const ok = await dialog.value?.modal() ?? false;
    return {
        ok,
        title: title.value,
        text: editor.value?.getHTML() ?? "",
        isPublic: isPublic.value,
    };
}

defineExpose({modal});
</script>

<style scoped lang="scss">

</style>
