<template>
    <BaseDialog
        :title="t('BlogPostDialog.title')"
        :ok-text="t('General.save')"
        ok-icon="fas fa-floppy-disk"
        :width="1000"
        ref="dialog"
    >
        <v-form>
            <v-text-field
                v-model="title"
                variant="outlined"
                :label="t('BlogPostDialog.labels.title')"
            />
            <QuillEditor
                theme="snow"
                style="height: 300px"
                content-type="html"
                v-model:content="text"
            />
            <v-switch v-model="isPublic" :label="switchLabel" />
        </v-form>
    </BaseDialog>
</template>

<script setup lang="ts">
import BaseDialog from "@/components/BaseDialog.vue";
import { QuillEditor } from "@vueup/vue-quill";
import { computed, type Ref, ref } from "vue";
import { useI18n } from "vue-i18n";
import type { BlogPost } from "@/apis/blog_api";

const dialog: Ref<InstanceType<typeof BaseDialog> | undefined> = ref(undefined);

const { t } = useI18n();
const isPublic = ref(false);
const title = ref("");
const text = ref("");
const switchLabel = computed(() =>
    isPublic.value
        ? t("BlogPostDialog.labels.postIsVisible")
        : t("BlogPostDialog.labels.postNotVisible")
);

async function modal(item: undefined | BlogPost = undefined) {
    title.value = item ? item.title : "";
    isPublic.value = item ? item.public : false;
    text.value = item ? item.text : "";
    const ok = (await dialog.value?.modal()) ?? false;
    return {
        ok,
        title: title.value,
        text: text.value,
        isPublic: isPublic.value,
    };
}

defineExpose({ modal });
</script>

<style scoped lang="scss"></style>
