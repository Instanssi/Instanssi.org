import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { defineComponent, h, type PropType } from "vue";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import MediaCell from "./MediaCell.vue";

const vuetify = createVuetify({ components, directives });

// Stub VDialog to avoid lifecycle issues in tests
const VDialogStub = defineComponent({
    name: "VDialog",
    props: {
        modelValue: { type: Boolean, default: false },
        maxWidth: { type: [Number, String] as PropType<number | string>, default: undefined },
    },
    emits: ["update:modelValue"],
    setup(props, { slots }) {
        return () =>
            h(
                "div",
                {
                    class: "v-dialog-stub",
                    "data-model-value": String(props.modelValue),
                    "data-max-width": String(props.maxWidth),
                },
                props.modelValue && slots.default ? slots.default() : undefined
            );
    },
});

function mountComponent(props: {
    url: string | null;
    filename?: string | null;
    size?: number;
    fallback?: string;
}) {
    return mount(MediaCell, {
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

describe("MediaCell", () => {
    describe("basic rendering", () => {
        it("renders fallback when url is null", () => {
            const wrapper = mountComponent({ url: null });
            expect(wrapper.text()).toBe("-");
            expect(wrapper.find(".media-cell").exists()).toBe(false);
        });

        it("renders custom fallback when url is null", () => {
            const wrapper = mountComponent({ url: null, fallback: "No file" });
            expect(wrapper.text()).toBe("No file");
        });

        it("renders media cell when url is provided", () => {
            const wrapper = mountComponent({ url: "https://example.com/file.jpg" });
            expect(wrapper.find(".media-cell").exists()).toBe(true);
        });
    });

    describe("image media type", () => {
        it("renders image thumbnail for image URLs", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg" });
            expect(wrapper.find(".image-thumbnail").exists()).toBe(true);
        });

        it("uses default size of 40 for images", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.png" });
            const img = wrapper.findComponent({ name: "VImg" });
            expect(img.props("width")).toBe(40);
            expect(img.props("height")).toBe(40);
        });

        it("uses custom size when provided for images", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.gif", size: 60 });
            const img = wrapper.findComponent({ name: "VImg" });
            expect(img.props("width")).toBe(60);
            expect(img.props("height")).toBe(60);
        });

        it("opens image preview dialog on click", async () => {
            const wrapper = mountComponent({ url: "https://example.com/image.webp" });
            await wrapper.find(".image-thumbnail").trigger("click");
            const dialogs = wrapper.findAll(".v-dialog-stub");
            const imageDialog = dialogs.find((d) => d.attributes("data-max-width") === "900");
            expect(imageDialog?.attributes("data-model-value")).toBe("true");
        });

        it("has accessible thumbnail for images", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.svg" });
            const thumbnail = wrapper.find(".image-thumbnail");
            expect(thumbnail.attributes("role")).toBe("button");
            expect(thumbnail.attributes("tabindex")).toBe("0");
        });
    });

    describe("video media type", () => {
        it("renders play button for video URLs", () => {
            const wrapper = mountComponent({ url: "https://example.com/video.mp4" });
            expect(wrapper.find(".image-thumbnail").exists()).toBe(false);
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons.length).toBeGreaterThan(0);
        });

        it("does not show filename link (download is in dialog)", () => {
            const wrapper = mountComponent({ url: "https://example.com/video.webm" });
            expect(wrapper.find(".filename-link").exists()).toBe(false);
        });

        it("opens video preview dialog on button click", async () => {
            const wrapper = mountComponent({ url: "https://example.com/video.mkv" });
            const playButton = wrapper.findComponent({ name: "VBtn" });
            await playButton.trigger("click");

            const dialogs = wrapper.findAll(".v-dialog-stub");
            const videoDialog = dialogs.find((d) => d.attributes("data-max-width") === "900");
            expect(videoDialog?.attributes("data-model-value")).toBe("true");
        });

        it("does not render video element when dialog is closed", () => {
            const wrapper = mountComponent({ url: "https://example.com/video.mov" });
            expect(wrapper.find("video").exists()).toBe(false);
        });
    });

    describe("audio media type", () => {
        it("renders audio button for audio URLs", () => {
            const wrapper = mountComponent({ url: "https://example.com/audio.mp3" });
            expect(wrapper.find(".image-thumbnail").exists()).toBe(false);
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons.length).toBeGreaterThan(0);
        });

        it("does not show filename link (download is in dialog)", () => {
            const wrapper = mountComponent({ url: "https://example.com/music.ogg" });
            expect(wrapper.find(".filename-link").exists()).toBe(false);
        });

        it("opens audio preview dialog on button click", async () => {
            const wrapper = mountComponent({ url: "https://example.com/sound.wav" });
            const playButton = wrapper.findComponent({ name: "VBtn" });
            await playButton.trigger("click");

            const dialogs = wrapper.findAll(".v-dialog-stub");
            const audioDialog = dialogs.find((d) => d.attributes("data-max-width") === "500");
            expect(audioDialog?.attributes("data-model-value")).toBe("true");
        });

        it("does not render audio element when dialog is closed", () => {
            const wrapper = mountComponent({ url: "https://example.com/audio.flac" });
            expect(wrapper.find("audio").exists()).toBe(false);
        });
    });

    describe("other media type", () => {
        it("renders icon button for non-media files", () => {
            const wrapper = mountComponent({ url: "https://example.com/document.pdf" });
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons.length).toBeGreaterThan(0);
        });

        it("does not show filename link (download is in dialog)", () => {
            const wrapper = mountComponent({ url: "https://example.com/archive.zip" });
            expect(wrapper.find(".filename-link").exists()).toBe(false);
        });

        it("opens file preview dialog on button click", async () => {
            const wrapper = mountComponent({ url: "https://example.com/data.json" });
            const button = wrapper.findComponent({ name: "VBtn" });
            await button.trigger("click");

            const dialogs = wrapper.findAll(".v-dialog-stub");
            const fileDialog = dialogs.find((d) => d.attributes("data-max-width") === "500");
            expect(fileDialog?.attributes("data-model-value")).toBe("true");
        });
    });

    describe("filename override", () => {
        it("uses custom filename when provided", async () => {
            const wrapper = mountComponent({
                url: "https://example.com/uuid-123.pdf",
                filename: "report.pdf",
            });
            const button = wrapper.findComponent({ name: "VBtn" });
            await button.trigger("click");
            expect(wrapper.text()).toContain("report.pdf");
            expect(wrapper.text()).not.toContain("uuid-123");
        });

        it("extracts filename from URL when not provided", async () => {
            const wrapper = mountComponent({
                url: "https://example.com/path/to/document.txt",
            });
            const button = wrapper.findComponent({ name: "VBtn" });
            await button.trigger("click");
            expect(wrapper.text()).toContain("document.txt");
        });
    });

    describe("media type detection edge cases", () => {
        it("handles uppercase extensions", () => {
            const wrapper = mountComponent({ url: "https://example.com/IMAGE.PNG" });
            expect(wrapper.find(".image-thumbnail").exists()).toBe(true);
        });

        it("handles URL with query parameters", () => {
            const wrapper = mountComponent({ url: "https://example.com/image.jpg?v=123" });
            expect(wrapper.find(".image-thumbnail").exists()).toBe(true);
        });

        it("handles relative URLs", () => {
            const wrapper = mountComponent({ url: "/media/uploads/video.mp4" });
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons.length).toBeGreaterThan(0);
        });
    });
});
