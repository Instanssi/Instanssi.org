<template>
    <v-dialog v-model="show" :width="width" :key="flushKey">
        <v-card>
            <v-card-title class="d-flex justify-space-between">
                <slot name="title">
                    <div class="justify-left">{{ title }}</div>
                    <div class="justify-end">
                        <v-btn
                            density="compact"
                            variant="text"
                            icon="fas fa-xmark"
                            @click="setResult(false)"
                        />
                    </div>
                </slot>
            </v-card-title>
            <v-divider role="presentation" />
            <v-card-text>
                <slot name="default" />
            </v-card-text>
            <v-card-actions class="justify-end">
                <slot name="buttons">
                    <v-btn variant="text" :prepend-icon="cancelIcon" @click="setResult(false)">
                        {{ cancelText ?? t("General.cancel") }}
                    </v-btn>
                    <v-btn
                        variant="elevated"
                        color="primary"
                        :prepend-icon="okIcon"
                        @click="setResult(true)"
                    >
                        {{ okText ?? t("General.ok") }}
                    </v-btn>
                </slot>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup lang="ts">
import { type Ref, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

interface Props {
    width?: number;
    title: string;
    cancelText?: string;
    cancelIcon?: string | undefined;
    okText?: string;
    okIcon?: string | undefined;
}
const emit = defineEmits<{
    open: [];
    close: [];
}>();
withDefaults(defineProps<Props>(), {
    width: 600,
    okText: undefined,
    okIcon: undefined,
    cancelText: undefined,
    cancelIcon: undefined,
});
defineExpose({ modal, setResult });

const flushKey = ref(0);
const show = ref(false);
const result: Ref<boolean | undefined> = ref(undefined);

async function modal(): Promise<boolean> {
    open();
    const output = await wait();
    close();
    return output ?? false;
}

function open() {
    flushKey.value += 1;
    result.value = undefined;
    emit("open");
    show.value = true;
}

function wait(): Promise<boolean | undefined> {
    return new Promise((resolve) => {
        watch(result, () => resolve(result.value));
    });
}

function close() {
    show.value = false;
    emit("close");
}

function setResult(ok: boolean): void {
    result.value = ok;
}
</script>

<style scoped lang="scss"></style>
