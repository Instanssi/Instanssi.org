import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import { ContentDialogStub, vuetify } from "@/test/helpers/component-stubs";

import ImagePreviewDialog from "./ImagePreviewDialog.vue";

function mountComponent(props: { modelValue: boolean; src: string | null | undefined }) {
    return mount(ImagePreviewDialog, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                ContentDialog: ContentDialogStub,
            },
        },
    });
}

describe("ImagePreviewDialog", () => {
    it("renders VImg with src prop when visible", () => {
        const wrapper = mountComponent({ modelValue: true, src: "https://example.com/image.jpg" });
        const img = wrapper.findComponent({ name: "VImg" });
        expect(img.exists()).toBe(true);
        expect(img.props("src")).toBe("https://example.com/image.jpg");
    });

    it("passes null src safely (coalesces to undefined)", () => {
        const wrapper = mountComponent({ modelValue: true, src: null });
        const img = wrapper.findComponent({ name: "VImg" });
        expect(img.exists()).toBe(true);
        // null ?? undefined yields undefined, but VImg may normalize to empty string
        expect(img.props("src")).toBeFalsy();
    });

    it("uses max-width 900", () => {
        const wrapper = mountComponent({ modelValue: true, src: "https://example.com/image.jpg" });
        const dialog = wrapper.find(".content-dialog-stub");
        expect(dialog.attributes("data-max-width")).toBe("900");
    });

    it("uses i18n title key PreviewDialog.imageTitle", () => {
        const wrapper = mountComponent({ modelValue: true, src: "https://example.com/image.jpg" });
        const dialog = wrapper.find(".content-dialog-stub");
        expect(dialog.attributes("data-title")).toBe("PreviewDialog.imageTitle");
    });

    it("does not render VImg when dialog is closed", () => {
        const wrapper = mountComponent({ modelValue: false, src: "https://example.com/image.jpg" });
        const img = wrapper.findComponent({ name: "VImg" });
        expect(img.exists()).toBe(false);
    });
});
