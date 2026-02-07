import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import { ContentDialogStub, vuetify } from "@/test/helpers/component-stubs";

import FilePreviewDialog from "./FilePreviewDialog.vue";

function mountComponent(props: {
    modelValue: boolean;
    downloadUrl: string;
    filename?: string | null;
}) {
    return mount(FilePreviewDialog, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                ContentDialog: ContentDialogStub,
            },
        },
    });
}

describe("FilePreviewDialog", () => {
    it("renders large file icon when visible", () => {
        const wrapper = mountComponent({
            modelValue: true,
            downloadUrl: "https://example.com/file.zip",
        });
        expect(wrapper.find(".file-icon").exists()).toBe(true);
    });

    it("shows filename when provided", () => {
        const wrapper = mountComponent({
            modelValue: true,
            downloadUrl: "https://example.com/file.zip",
            filename: "archive.zip",
        });
        expect(wrapper.text()).toContain("archive.zip");
    });

    it("does not show filename when not provided", () => {
        const wrapper = mountComponent({
            modelValue: true,
            downloadUrl: "https://example.com/file.zip",
        });
        expect(wrapper.find("span.mt-4").exists()).toBe(false);
    });

    it("uses max-width 500", () => {
        const wrapper = mountComponent({
            modelValue: true,
            downloadUrl: "https://example.com/file.zip",
        });
        const dialog = wrapper.find(".content-dialog-stub");
        expect(dialog.attributes("data-max-width")).toBe("500");
    });

    it("uses i18n title key PreviewDialog.fileTitle", () => {
        const wrapper = mountComponent({
            modelValue: true,
            downloadUrl: "https://example.com/file.zip",
        });
        const dialog = wrapper.find(".content-dialog-stub");
        expect(dialog.attributes("data-title")).toBe("PreviewDialog.fileTitle");
    });

    it("does not render content when dialog is closed", () => {
        const wrapper = mountComponent({
            modelValue: false,
            downloadUrl: "https://example.com/file.zip",
            filename: "archive.zip",
        });
        expect(wrapper.text()).not.toContain("archive.zip");
    });
});
