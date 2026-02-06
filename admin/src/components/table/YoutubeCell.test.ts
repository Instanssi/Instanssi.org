import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import { VDialogStub, vuetify } from "@/test/helpers/component-stubs";

import YoutubeCell from "./YoutubeCell.vue";

function mountComponent(props: { value?: string | null; fallback?: string }) {
    return mount(YoutubeCell, {
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

describe("YoutubeCell", () => {
    describe("fallback rendering", () => {
        it("renders fallback text when value is null", () => {
            const wrapper = mountComponent({ value: null });
            expect(wrapper.text()).toBe("-");
        });

        it("renders custom fallback text", () => {
            const wrapper = mountComponent({ value: null, fallback: "No video" });
            expect(wrapper.text()).toBe("No video");
        });

        it("renders fallback for invalid URLs", () => {
            const wrapper = mountComponent({ value: "not-a-url" });
            expect(wrapper.text()).toBe("-");
        });
    });

    describe("video ID parsing", () => {
        it("parses video ID from YouTube URL", () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            expect(wrapper.text()).toContain("dQw4w9WgXcQ");
        });

        it("displays video ID as clickable link", () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            const link = wrapper.find("a");
            expect(link.exists()).toBe(true);
            expect(link.text()).toBe("dQw4w9WgXcQ");
        });
    });

    describe("start time", () => {
        it("parses and displays start time", () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ&start=90",
            });
            expect(wrapper.text()).toContain("@ 1:30");
        });

        it("formats start time as m:ss", () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=abc123&start=65",
            });
            expect(wrapper.text()).toContain("@ 1:05");
        });

        it("formats start time as h:mm:ss", () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=abc123&start=3661",
            });
            expect(wrapper.text()).toContain("@ 1:01:01");
        });

        it("does not show time when start is absent", () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            expect(wrapper.text()).not.toContain("@");
        });
    });

    describe("external link", () => {
        it("external link points to original URL", () => {
            const url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
            const wrapper = mountComponent({ value: url });
            const externalLink = wrapper.find("a.external-link");
            expect(externalLink.exists()).toBe(true);
            expect(externalLink.attributes("href")).toBe(url);
            expect(externalLink.attributes("target")).toBe("_blank");
        });
    });

    describe("dialog behavior", () => {
        it("opens dialog on video ID click", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            const videoLink = wrapper.find("a[href='#']");
            await videoLink.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.attributes("data-model-value")).toBe("true");
        });

        it("dialog receives video ID as title", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            const videoLink = wrapper.find("a[href='#']");
            await videoLink.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            // ContentDialog title prop receives videoId; it renders in v-card-title
            expect(dialog.text()).toContain("dQw4w9WgXcQ");
        });

        it("does not render iframe when dialog is closed", () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            expect(wrapper.find("iframe").exists()).toBe(false);
        });

        it("renders iframe with embed URL when dialog is open", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            const videoLink = wrapper.find("a[href='#']");
            await videoLink.trigger("click");
            const iframe = wrapper.find("iframe");
            expect(iframe.exists()).toBe(true);
            expect(iframe.attributes("src")).toBe("https://www.youtube.com/embed/dQw4w9WgXcQ");
        });

        it("embed URL includes start time when present", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ&start=30",
            });
            const videoLink = wrapper.find("a[href='#']");
            await videoLink.trigger("click");
            const iframe = wrapper.find("iframe");
            expect(iframe.attributes("src")).toBe(
                "https://www.youtube.com/embed/dQw4w9WgXcQ?start=30"
            );
        });

        it("dialog uses max-width 800", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            const videoLink = wrapper.find("a[href='#']");
            await videoLink.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.attributes("data-max-width")).toBe("800");
        });
    });
});
