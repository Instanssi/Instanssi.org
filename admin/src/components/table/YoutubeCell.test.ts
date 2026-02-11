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

    describe("icon button rendering", () => {
        it("renders icon button for valid YouTube URL", () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            const btn = wrapper.findComponent({ name: "VBtn" });
            expect(btn.exists()).toBe(true);
        });

        it("does not show video ID as text in the cell", () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            expect(wrapper.text()).not.toContain("dQw4w9WgXcQ");
        });

        it("button has title attribute for accessibility", () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            const btn = wrapper.findComponent({ name: "VBtn" });
            expect(btn.attributes("title")).toBe("General.clickToPreview");
        });
    });

    describe("dialog behavior", () => {
        it("opens dialog on button click", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.attributes("data-model-value")).toBe("true");
        });

        it("dialog uses max-width 800", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.attributes("data-max-width")).toBe("800");
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
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const iframe = wrapper.find("iframe");
            expect(iframe.exists()).toBe(true);
            expect(iframe.attributes("src")).toBe("https://www.youtube.com/embed/dQw4w9WgXcQ");
        });

        it("embed URL includes start time when present", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ&start=30",
            });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const iframe = wrapper.find("iframe");
            expect(iframe.attributes("src")).toBe(
                "https://www.youtube.com/embed/dQw4w9WgXcQ?start=30"
            );
        });
    });

    describe("dialog title with start time", () => {
        it("dialog title shows base title without start time", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.text()).toContain("YoutubeCell.dialogTitle");
            expect(dialog.text()).not.toContain("@");
        });

        it("dialog title includes formatted start time", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ&start=90",
            });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.text()).toContain("@ 1:30");
        });

        it("dialog title formats hours for large start times", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=abc123&start=3661",
            });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.text()).toContain("@ 1:01:01");
        });
    });

    describe("external link in dialog title", () => {
        it("dialog contains YouTube link button to original URL", async () => {
            const url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
            const wrapper = mountComponent({ value: url });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            const youtubeBtn = buttons.find((b) => b.text().includes("YouTube"));
            expect(youtubeBtn).toBeDefined();
            expect(youtubeBtn!.attributes("href")).toBe(url);
        });

        it("YouTube link button shows label text", async () => {
            const wrapper = mountComponent({
                value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            const youtubeBtn = buttons.find((b) => b.text().includes("YouTube"));
            expect(youtubeBtn).toBeDefined();
        });
    });
});
