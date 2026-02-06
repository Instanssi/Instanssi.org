/**
 * Shared component stubs for dialog tests.
 *
 * VDialogStub replaces Vuetify's VDialog to avoid lifecycle issues in unit tests.
 * ContentDialogStub replaces ContentDialog for testing components that use it.
 *
 * Both stubs expose relevant props as data-* attributes for assertions and
 * conditionally render their default slot based on modelValue.
 */
import { defineComponent, h, type PropType } from "vue";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

export const vuetify = createVuetify({ components, directives });

export const VDialogStub = defineComponent({
    name: "VDialog",
    props: {
        modelValue: { type: Boolean, default: false },
        width: { type: [Number, String] as PropType<number | string>, default: undefined },
        maxWidth: { type: [Number, String] as PropType<number | string>, default: undefined },
        scrollable: { type: Boolean, default: false },
    },
    emits: ["update:modelValue"],
    setup(props, { slots }) {
        return () =>
            h(
                "div",
                {
                    class: "v-dialog-stub",
                    "data-model-value": String(props.modelValue),
                    "data-width": String(props.width),
                    "data-max-width": String(props.maxWidth),
                    "data-scrollable": String(props.scrollable),
                },
                props.modelValue && slots.default ? slots.default() : undefined
            );
    },
});

export const ContentDialogStub = defineComponent({
    name: "ContentDialog",
    props: {
        modelValue: { type: Boolean, default: false },
        title: { type: String, default: "" },
        maxWidth: { type: Number as PropType<number>, default: undefined },
    },
    emits: ["update:modelValue"],
    setup(props, { slots }) {
        return () =>
            h(
                "div",
                {
                    class: "content-dialog-stub",
                    "data-model-value": String(props.modelValue),
                    "data-title": props.title,
                    "data-max-width": String(props.maxWidth),
                },
                props.modelValue && slots.default ? slots.default() : undefined
            );
    },
});
