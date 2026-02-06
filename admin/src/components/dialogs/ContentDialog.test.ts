import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import { VDialogStub, vuetify } from "@/test/helpers/component-stubs";

import ContentDialog from "./ContentDialog.vue";

function mountComponent(props: {
    modelValue: boolean;
    title: string;
    maxWidth?: number;
    scrollable?: boolean;
    contentClass?: string;
}) {
    return mount(ContentDialog, {
        props,
        slots: {
            default: "<p>Slot content</p>",
        },
        global: {
            plugins: [vuetify],
            stubs: {
                FontAwesomeIcon: true,
                VDialog: VDialogStub,
            },
        },
    });
}

describe("ContentDialog", () => {
    it("renders title text from prop", () => {
        const wrapper = mountComponent({ modelValue: true, title: "My Title" });
        expect(wrapper.text()).toContain("My Title");
    });

    it("renders slot content inside v-card-text", () => {
        const wrapper = mountComponent({ modelValue: true, title: "Title" });
        const cardText = wrapper.findComponent({ name: "VCardText" });
        expect(cardText.text()).toContain("Slot content");
    });

    it("passes default maxWidth of 600 to v-dialog", () => {
        const wrapper = mountComponent({ modelValue: true, title: "Title" });
        const dialog = wrapper.find(".v-dialog-stub");
        expect(dialog.attributes("data-max-width")).toBe("600");
    });

    it("passes custom maxWidth to v-dialog", () => {
        const wrapper = mountComponent({ modelValue: true, title: "Title", maxWidth: 900 });
        const dialog = wrapper.find(".v-dialog-stub");
        expect(dialog.attributes("data-max-width")).toBe("900");
    });

    it("passes default scrollable false to v-dialog", () => {
        const wrapper = mountComponent({ modelValue: true, title: "Title" });
        const dialog = wrapper.find(".v-dialog-stub");
        expect(dialog.attributes("data-scrollable")).toBe("false");
    });

    it("passes scrollable true to v-dialog", () => {
        const wrapper = mountComponent({ modelValue: true, title: "Title", scrollable: true });
        const dialog = wrapper.find(".v-dialog-stub");
        expect(dialog.attributes("data-scrollable")).toBe("true");
    });

    it("close button emits update:modelValue with false", async () => {
        const wrapper = mountComponent({ modelValue: true, title: "Title" });
        const closeBtn = wrapper.findComponent({ name: "VBtn" });
        await closeBtn.trigger("click");
        expect(wrapper.emitted("update:modelValue")).toBeTruthy();
        expect(wrapper.emitted("update:modelValue")![0]).toEqual([false]);
    });

    it("is hidden when modelValue is false", () => {
        const wrapper = mountComponent({ modelValue: false, title: "Title" });
        const dialog = wrapper.find(".v-dialog-stub");
        expect(dialog.attributes("data-model-value")).toBe("false");
        expect(wrapper.text()).not.toContain("Slot content");
    });

    it("is visible when modelValue is true", () => {
        const wrapper = mountComponent({ modelValue: true, title: "Title" });
        const dialog = wrapper.find(".v-dialog-stub");
        expect(dialog.attributes("data-model-value")).toBe("true");
        expect(wrapper.text()).toContain("Slot content");
    });

    it("applies contentClass to v-card-text", () => {
        const wrapper = mountComponent({ modelValue: true, title: "Title", contentClass: "pa-0" });
        const cardText = wrapper.findComponent({ name: "VCardText" });
        expect(cardText.classes()).toContain("pa-0");
    });

    it("does not add extra class to v-card-text by default", () => {
        const wrapper = mountComponent({ modelValue: true, title: "Title" });
        const cardText = wrapper.findComponent({ name: "VCardText" });
        expect(cardText.classes()).not.toContain("pa-0");
    });
});
