import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import { ContentDialogStub, vuetify } from "@/test/helpers/component-stubs";

import AudioPreviewDialog from "./AudioPreviewDialog.vue";

function mountComponent(props: { modelValue: boolean; src: string | null | undefined }) {
    return mount(AudioPreviewDialog, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                ContentDialog: ContentDialogStub,
            },
        },
    });
}

describe("AudioPreviewDialog", () => {
    it("does not render audio element when dialog is closed", () => {
        const wrapper = mountComponent({ modelValue: false, src: "https://example.com/audio.mp3" });
        expect(wrapper.find("audio").exists()).toBe(false);
    });

    it("renders audio with correct src, controls, and autoplay when visible", () => {
        const wrapper = mountComponent({ modelValue: true, src: "https://example.com/audio.mp3" });
        const audio = wrapper.find("audio");
        expect(audio.exists()).toBe(true);
        expect(audio.attributes("src")).toBe("https://example.com/audio.mp3");
        expect(audio.attributes("controls")).toBeDefined();
        expect(audio.attributes("autoplay")).toBeDefined();
    });

    it("uses max-width 500", () => {
        const wrapper = mountComponent({ modelValue: true, src: "https://example.com/audio.mp3" });
        const dialog = wrapper.find(".content-dialog-stub");
        expect(dialog.attributes("data-max-width")).toBe("500");
    });

    it("uses i18n title key PreviewDialog.audioTitle", () => {
        const wrapper = mountComponent({ modelValue: true, src: "https://example.com/audio.mp3" });
        const dialog = wrapper.find(".content-dialog-stub");
        expect(dialog.attributes("data-title")).toBe("PreviewDialog.audioTitle");
    });

    it("does not render audio element when src is null", () => {
        const wrapper = mountComponent({ modelValue: true, src: null });
        expect(wrapper.find("audio").exists()).toBe(false);
    });
});
