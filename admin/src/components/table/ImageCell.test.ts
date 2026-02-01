import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { defineComponent, h } from "vue";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import ImageCell from "./ImageCell.vue";

const vuetify = createVuetify({ components, directives });

// Stub VDialog to avoid lifecycle issues in tests
const VDialogStub = defineComponent({
    name: "VDialog",
    props: {
        modelValue: { type: Boolean, default: false },
    },
    emits: ["update:modelValue"],
    setup(props, { slots }) {
        return () =>
            h(
                "div",
                { class: "v-dialog-stub", "data-model-value": String(props.modelValue) },
                props.modelValue && slots.default ? slots.default() : undefined
            );
    },
});

function mountComponent(props: { url: string | null; size?: number }) {
    return mount(ImageCell, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                FontAwesomeIcon: true,
                VDialog: VDialogStub,
            },
        },
    });
}

describe("ImageCell", () => {
    describe("basic rendering", () => {
        it("renders placeholder icon when url is null", () => {
            const wrapper = mountComponent({ url: null });
            expect(wrapper.find(".image-placeholder").exists()).toBe(true);
            expect(wrapper.find(".image-cell").exists()).toBe(false);
            expect(wrapper.findComponent({ name: "FontAwesomeIcon" }).exists()).toBe(true);
        });

        it("placeholder uses default size of 40", () => {
            const wrapper = mountComponent({ url: null });
            const placeholder = wrapper.find(".image-placeholder");
            expect(placeholder.attributes("style")).toContain("width: 40px");
            expect(placeholder.attributes("style")).toContain("height: 40px");
        });

        it("placeholder uses custom size when provided", () => {
            const wrapper = mountComponent({ url: null, size: 60 });
            const placeholder = wrapper.find(".image-placeholder");
            expect(placeholder.attributes("style")).toContain("width: 60px");
            expect(placeholder.attributes("style")).toContain("height: 60px");
        });

        it("renders image thumbnail when url is provided", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg" });
            expect(wrapper.find(".image-cell").exists()).toBe(true);
            expect(wrapper.find(".image-thumbnail").exists()).toBe(true);
        });

        it("uses default size of 40", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg" });
            const img = wrapper.findComponent({ name: "VImg" });
            expect(img.props("width")).toBe(40);
            expect(img.props("height")).toBe(40);
        });

        it("uses custom size when provided", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg", size: 60 });
            const img = wrapper.findComponent({ name: "VImg" });
            expect(img.props("width")).toBe(60);
            expect(img.props("height")).toBe(60);
        });
    });

    describe("accessibility", () => {
        it("has role button on thumbnail", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg" });
            const thumbnail = wrapper.find(".image-thumbnail");
            expect(thumbnail.attributes("role")).toBe("button");
        });

        it("has tabindex for keyboard navigation", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg" });
            const thumbnail = wrapper.find(".image-thumbnail");
            expect(thumbnail.attributes("tabindex")).toBe("0");
        });

        it("has title attribute", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg" });
            const thumbnail = wrapper.find(".image-thumbnail");
            expect(thumbnail.attributes("title")).toBeTruthy();
        });
    });

    describe("preview dialog", () => {
        it("dialog is initially closed", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg" });
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.attributes("data-model-value")).toBe("false");
        });

        it("opens dialog on click", async () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg" });
            await wrapper.find(".image-thumbnail").trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.attributes("data-model-value")).toBe("true");
        });

        it("opens dialog on Enter key", async () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg" });
            await wrapper.find(".image-thumbnail").trigger("keydown.enter");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.attributes("data-model-value")).toBe("true");
        });

        it("opens dialog on Space key", async () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg" });
            await wrapper.find(".image-thumbnail").trigger("keydown.space");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.attributes("data-model-value")).toBe("true");
        });
    });
});
