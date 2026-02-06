import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import { ContentDialogStub, vuetify } from "@/test/helpers/component-stubs";

import VideoPreviewDialog from "./VideoPreviewDialog.vue";

function mountComponent(props: { modelValue: boolean; src: string | null | undefined }) {
    return mount(VideoPreviewDialog, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                ContentDialog: ContentDialogStub,
            },
        },
    });
}

describe("VideoPreviewDialog", () => {
    it("does not render video element when dialog is closed", () => {
        const wrapper = mountComponent({ modelValue: false, src: "https://example.com/video.mp4" });
        expect(wrapper.find("video").exists()).toBe(false);
    });

    it("renders video with correct src, controls, and autoplay when visible", () => {
        const wrapper = mountComponent({ modelValue: true, src: "https://example.com/video.mp4" });
        const video = wrapper.find("video");
        expect(video.exists()).toBe(true);
        expect(video.attributes("src")).toBe("https://example.com/video.mp4");
        expect(video.attributes("controls")).toBeDefined();
        expect(video.attributes("autoplay")).toBeDefined();
    });

    it("uses max-width 900", () => {
        const wrapper = mountComponent({ modelValue: true, src: "https://example.com/video.mp4" });
        const dialog = wrapper.find(".content-dialog-stub");
        expect(dialog.attributes("data-max-width")).toBe("900");
    });

    it("uses i18n title key PreviewDialog.videoTitle", () => {
        const wrapper = mountComponent({ modelValue: true, src: "https://example.com/video.mp4" });
        const dialog = wrapper.find(".content-dialog-stub");
        expect(dialog.attributes("data-title")).toBe("PreviewDialog.videoTitle");
    });

    it("does not render video element when src is null", () => {
        const wrapper = mountComponent({ modelValue: true, src: null });
        expect(wrapper.find("video").exists()).toBe(false);
    });
});
