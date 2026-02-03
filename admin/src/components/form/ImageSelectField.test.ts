import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import ImageSelectField, { type ImageSelectItem } from "./ImageSelectField.vue";

const vuetify = createVuetify({ components, directives });

function mountComponent(props: {
    modelValue: string | null;
    items: ImageSelectItem[];
    label?: string;
    placeholder?: string;
    noDataText?: string;
    loading?: boolean;
    showPreview?: boolean;
    thumbnailSize?: number;
    previewMaxHeight?: number;
}) {
    return mount(ImageSelectField, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                FontAwesomeIcon: true,
                // Stub expand transition to render children immediately
                VExpandTransition: {
                    template: "<div><slot /></div>",
                },
            },
        },
    });
}

const testItems: ImageSelectItem[] = [
    { title: "Image 1", value: "https://example.com/image1.png" },
    { title: "Image 2", value: "https://example.com/image2.png" },
    { title: "Image 3", value: "https://example.com/image3.jpg" },
];

describe("ImageSelectField", () => {
    describe("rendering", () => {
        it("renders v-select with label", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                items: testItems,
                label: "Select Image",
            });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.exists()).toBe(true);
            expect(select.props("label")).toBe("Select Image");
        });

        it("renders with placeholder", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                items: testItems,
                placeholder: "Choose an image",
            });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("placeholder")).toBe("Choose an image");
        });

        it("renders with noDataText", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                items: [],
                noDataText: "No images available",
            });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("noDataText")).toBe("No images available");
        });

        it("shows loading state", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                items: [],
                loading: true,
            });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("loading")).toBe(true);
        });

        it("passes items to v-select", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                items: testItems,
            });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("items")).toEqual(testItems);
        });
    });

    describe("preview", () => {
        it("shows preview when value is selected and showPreview is true", async () => {
            const wrapper = mountComponent({
                modelValue: "https://example.com/image1.png",
                items: testItems,
                showPreview: true,
            });
            await flushPromises();

            // Find the preview container (div with mt-2 class inside the expand transition)
            const previewContainer = wrapper.find(".mt-2");
            expect(previewContainer.exists()).toBe(true);

            // Find the preview image inside it
            const previewImage = previewContainer.findComponent({ name: "VImg" });
            expect(previewImage.exists()).toBe(true);
            expect(previewImage.props("src")).toBe("https://example.com/image1.png");
        });

        it("hides preview when showPreview is false", async () => {
            const wrapper = mountComponent({
                modelValue: "https://example.com/image1.png",
                items: testItems,
                showPreview: false,
            });
            await flushPromises();

            // The preview container should not be rendered
            const previewContainer = wrapper.find(".mt-2");
            expect(previewContainer.exists()).toBe(false);
        });

        it("hides preview when no value is selected", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                items: testItems,
                showPreview: true,
            });
            await flushPromises();

            // The preview container should not be rendered
            const previewContainer = wrapper.find(".mt-2");
            expect(previewContainer.exists()).toBe(false);
        });

        it("uses custom previewMaxHeight", async () => {
            const wrapper = mountComponent({
                modelValue: "https://example.com/image1.png",
                items: testItems,
                showPreview: true,
                previewMaxHeight: 300,
            });
            await flushPromises();

            const previewContainer = wrapper.find(".mt-2");
            const previewImage = previewContainer.findComponent({ name: "VImg" });
            expect(previewImage.props("maxHeight")).toBe(300);
        });

        it("uses default previewMaxHeight of 200", async () => {
            const wrapper = mountComponent({
                modelValue: "https://example.com/image1.png",
                items: testItems,
                showPreview: true,
            });
            await flushPromises();

            const previewContainer = wrapper.find(".mt-2");
            const previewImage = previewContainer.findComponent({ name: "VImg" });
            expect(previewImage.props("maxHeight")).toBe(200);
        });
    });

    describe("events", () => {
        it("emits update:modelValue when selection changes", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                items: testItems,
            });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.vm.$emit("update:modelValue", "https://example.com/image2.png");

            expect(wrapper.emitted("update:modelValue")).toBeTruthy();
            expect(wrapper.emitted("update:modelValue")![0]).toEqual([
                "https://example.com/image2.png",
            ]);
        });

        it("emits null when selection is cleared", async () => {
            const wrapper = mountComponent({
                modelValue: "https://example.com/image1.png",
                items: testItems,
            });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.vm.$emit("update:modelValue", null);

            expect(wrapper.emitted("update:modelValue")).toBeTruthy();
            expect(wrapper.emitted("update:modelValue")![0]).toEqual([null]);
        });
    });

    describe("thumbnail configuration", () => {
        it("uses default thumbnailSize of 40", async () => {
            const wrapper = mountComponent({
                modelValue: "https://example.com/image1.png",
                items: testItems,
            });
            await flushPromises();

            // Find thumbnail images (not the preview which uses contain)
            const images = wrapper.findAllComponents({ name: "VImg" });
            const thumbnailImage = images.find((img) => img.props("cover") === true);
            expect(thumbnailImage).toBeTruthy();
            expect(thumbnailImage!.props("width")).toBe(40);
            expect(thumbnailImage!.props("height")).toBe(40);
        });

        it("uses custom thumbnailSize", async () => {
            const wrapper = mountComponent({
                modelValue: "https://example.com/image1.png",
                items: testItems,
                thumbnailSize: 60,
            });
            await flushPromises();

            const images = wrapper.findAllComponents({ name: "VImg" });
            const thumbnailImage = images.find((img) => img.props("cover") === true);
            expect(thumbnailImage).toBeTruthy();
            expect(thumbnailImage!.props("width")).toBe(60);
            expect(thumbnailImage!.props("height")).toBe(60);
        });
    });

    describe("default props", () => {
        it("showPreview defaults to true", async () => {
            const wrapper = mountComponent({
                modelValue: "https://example.com/image1.png",
                items: testItems,
            });
            await flushPromises();

            // Preview should be visible by default
            const previewContainer = wrapper.find(".mt-2");
            expect(previewContainer.exists()).toBe(true);
        });

        it("loading defaults to false", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                items: testItems,
            });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("loading")).toBe(false);
        });
    });
});
