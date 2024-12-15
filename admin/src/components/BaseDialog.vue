<template>
    <v-dialog :key="flushKey" v-model="show" :width="width">
        <v-card>
            <v-card-title class="d-flex justify-space-between">
                <slot name="title">
                    <div class="justify-left">
                        {{ title }}
                    </div>
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
            <slot name="default" />
        </v-card>
    </v-dialog>
</template>

<script setup lang="ts">
import { type Ref, ref, watch } from "vue";

interface Props {
    width?: number;
    title: string;
}
const emit = defineEmits<{
    open: [];
    close: [];
}>();
withDefaults(defineProps<Props>(), {
    width: 600,
});

const flushKey = ref(0);
const show = ref(false);
const result: Ref<boolean | undefined> = ref(undefined);

defineExpose({ modal, setResult });

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
        watch([result, show], () => resolve(result.value ?? false));
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
