import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import { type FileValue } from "@/utils/file";

import FileUploadField from "./FileUploadField.vue";

const vuetify = createVuetify({ components, directives });

// Track created object URLs for cleanup verification
const createdObjectUrls: string[] = [];
const revokedObjectUrls: string[] = [];

// Mock URL.createObjectURL and URL.revokeObjectURL
const originalCreateObjectURL = URL.createObjectURL;
const originalRevokeObjectURL = URL.revokeObjectURL;

beforeEach(() => {
    createdObjectUrls.length = 0;
    revokedObjectUrls.length = 0;

    URL.createObjectURL = vi.fn((_blob: Blob) => {
        const url = `blob:test-${createdObjectUrls.length}`;
        createdObjectUrls.push(url);
        return url;
    });

    URL.revokeObjectURL = vi.fn((url: string) => {
        revokedObjectUrls.push(url);
    });
});

afterEach(() => {
    URL.createObjectURL = originalCreateObjectURL;
    URL.revokeObjectURL = originalRevokeObjectURL;
});

function mountComponent(props: {
    modelValue: FileValue;
    label: string;
    currentFileUrl?: string | null;
    errorMessage?: string;
    accept?: string;
    required?: boolean;
}) {
    return mount(FileUploadField, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                FontAwesomeIcon: true,
            },
        },
    });
}

describe("FileUploadField", () => {
    describe("basic rendering", () => {
        it("renders file input with label", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                label: "Upload File",
            });
            await flushPromises();

            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            expect(fileInput.exists()).toBe(true);
            expect(fileInput.props("label")).toBe("Upload File");
        });

        it("adds asterisk to label when required", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                label: "Upload File",
                required: true,
            });
            await flushPromises();

            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            expect(fileInput.props("label")).toBe("Upload File *");
        });

        it("shows error message when provided", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                label: "Upload File",
                errorMessage: "File is required",
            });
            await flushPromises();

            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            expect(fileInput.props("errorMessages")).toBe("File is required");
        });

        it("uses custom accept attribute", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                label: "Upload File",
                accept: ".zip,.7z",
            });
            await flushPromises();

            const input = wrapper.find('input[type="file"]');
            expect(input.attributes("accept")).toBe(".zip,.7z");
        });
    });

    describe("file type detection", () => {
        it("shows image preview for image files", async () => {
            const file = new File(["test"], "test.png", { type: "image/png" });

            const wrapper = mountComponent({
                modelValue: file,
                label: "Upload File",
            });
            await flushPromises();

            const preview = wrapper.find(".file-preview");
            expect(preview.exists()).toBe(true);

            const img = preview.findComponent({ name: "VImg" });
            expect(img.exists()).toBe(true);
        });

        it("shows video button for video files", async () => {
            const file = new File(["test"], "test.mp4", { type: "video/mp4" });

            const wrapper = mountComponent({
                modelValue: file,
                label: "Upload File",
            });
            await flushPromises();

            // Should have a button (not image preview)
            expect(wrapper.find(".file-preview").exists()).toBe(false);
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons.length).toBeGreaterThan(0);
        });

        it("shows audio button for audio files", async () => {
            const file = new File(["test"], "test.mp3", { type: "audio/mpeg" });

            const wrapper = mountComponent({
                modelValue: file,
                label: "Upload File",
            });
            await flushPromises();

            expect(wrapper.find(".file-preview").exists()).toBe(false);
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons.length).toBeGreaterThan(0);
        });

        it("shows download button for other files", async () => {
            const file = new File(["test"], "test.zip", {
                type: "application/zip",
            });

            const wrapper = mountComponent({
                modelValue: file,
                label: "Upload File",
            });
            await flushPromises();

            expect(wrapper.find(".file-preview").exists()).toBe(false);
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons.length).toBeGreaterThan(0);
        });

        it("detects image type from extension when MIME is missing", async () => {
            const file = new File(["test"], "test.jpg", { type: "" });

            const wrapper = mountComponent({
                modelValue: file,
                label: "Upload File",
            });
            await flushPromises();

            const preview = wrapper.find(".file-preview");
            expect(preview.exists()).toBe(true);
        });

        it("detects video type from extension when MIME is missing", async () => {
            const file = new File(["test"], "test.mkv", { type: "" });

            const wrapper = mountComponent({
                modelValue: file,
                label: "Upload File",
            });
            await flushPromises();

            // No image preview for video
            expect(wrapper.find(".file-preview").exists()).toBe(false);
        });
    });

    describe("current file URL", () => {
        it("shows preview for current image URL", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                label: "Upload File",
                currentFileUrl: "https://example.com/image.jpg",
            });
            await flushPromises();

            const preview = wrapper.find(".file-preview");
            expect(preview.exists()).toBe(true);
        });

        it("shows download button for current non-media URL", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                label: "Upload File",
                currentFileUrl: "https://example.com/document.pdf",
            });
            await flushPromises();

            expect(wrapper.find(".file-preview").exists()).toBe(false);
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons.length).toBeGreaterThan(0);
        });

        it("prefers selected file over current URL", async () => {
            const file = new File(["test"], "new.png", { type: "image/png" });

            const wrapper = mountComponent({
                modelValue: file,
                label: "Upload File",
                currentFileUrl: "https://example.com/old.jpg",
            });
            await flushPromises();

            // Should use the object URL from the file
            const img = wrapper.find(".file-preview").findComponent({ name: "VImg" });
            expect(img.props("src")).toBe("blob:test-0");
        });
    });

    describe("clearing files", () => {
        it("emits update:modelValue with null when cleared", async () => {
            const file = new File(["test"], "test.png", { type: "image/png" });

            const wrapper = mountComponent({
                modelValue: file,
                label: "Upload File",
            });
            await flushPromises();

            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.vm.$emit("click:clear");

            expect(wrapper.emitted("update:modelValue")).toBeTruthy();
            expect(wrapper.emitted("update:modelValue")![0]).toEqual([null]);
        });

        it("hides preview after clearing", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                label: "Upload File",
                currentFileUrl: "https://example.com/image.jpg",
            });
            await flushPromises();

            expect(wrapper.find(".file-preview").exists()).toBe(true);

            // Simulate clear
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.vm.$emit("click:clear");
            await flushPromises();

            expect(wrapper.find(".file-preview").exists()).toBe(false);
        });
    });

    describe("object URL lifecycle", () => {
        it("creates object URL for selected file", async () => {
            const file = new File(["test"], "test.png", { type: "image/png" });

            mountComponent({
                modelValue: file,
                label: "Upload File",
            });
            await flushPromises();

            expect(URL.createObjectURL).toHaveBeenCalledWith(file);
            expect(createdObjectUrls.length).toBe(1);
        });

        it("revokes object URL when file changes", async () => {
            const file1 = new File(["test1"], "test1.png", { type: "image/png" });
            const file2 = new File(["test2"], "test2.png", { type: "image/png" });

            const wrapper = mountComponent({
                modelValue: file1,
                label: "Upload File",
            });
            await flushPromises();
            expect(createdObjectUrls.length).toBe(1);

            await wrapper.setProps({ modelValue: file2 });
            await flushPromises();

            expect(revokedObjectUrls.length).toBe(1);
            expect(createdObjectUrls.length).toBe(2);
        });

        it("revokes object URL on unmount", async () => {
            const file = new File(["test"], "test.png", { type: "image/png" });

            const wrapper = mountComponent({
                modelValue: file,
                label: "Upload File",
            });
            await flushPromises();

            wrapper.unmount();

            expect(revokedObjectUrls.length).toBe(1);
        });
    });

    describe("emitting events", () => {
        it("emits update:modelValue when file is selected", async () => {
            const wrapper = mountComponent({
                modelValue: null,
                label: "Upload File",
            });
            await flushPromises();

            const file = new File(["test"], "test.png", { type: "image/png" });
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.vm.$emit("update:modelValue", file);

            expect(wrapper.emitted("update:modelValue")).toBeTruthy();
            expect(wrapper.emitted("update:modelValue")![0]).toEqual([file]);
        });
    });
});
