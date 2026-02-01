import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import ImageUploadField from "./ImageUploadField.vue";

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
    modelValue: File | File[] | null;
    label: string;
    currentImageUrl?: string | null;
    errorMessage?: string;
    accept?: string;
    required?: boolean;
}) {
    return mount(ImageUploadField, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                FontAwesomeIcon: true,
            },
        },
    });
}

describe("ImageUploadField", () => {
    it("renders file input with label", async () => {
        const wrapper = mountComponent({
            modelValue: null,
            label: "Upload Image",
        });
        await flushPromises();

        const fileInput = wrapper.findComponent({ name: "VFileInput" });
        expect(fileInput.exists()).toBe(true);
        expect(fileInput.props("label")).toBe("Upload Image");
    });

    it("adds asterisk to label when required", async () => {
        const wrapper = mountComponent({
            modelValue: null,
            label: "Upload Image",
            required: true,
        });
        await flushPromises();

        const fileInput = wrapper.findComponent({ name: "VFileInput" });
        expect(fileInput.props("label")).toBe("Upload Image *");
    });

    it("shows thumbnail when currentImageUrl is provided", async () => {
        const wrapper = mountComponent({
            modelValue: null,
            label: "Upload Image",
            currentImageUrl: "https://example.com/image.jpg",
        });
        await flushPromises();

        const preview = wrapper.find(".image-preview");
        expect(preview.exists()).toBe(true);

        // Find the VImg inside the preview
        const img = preview.findComponent({ name: "VImg" });
        expect(img.exists()).toBe(true);
        expect(img.props("src")).toBe("https://example.com/image.jpg");
    });

    it("does not show thumbnail when no image URL and no file selected", async () => {
        const wrapper = mountComponent({
            modelValue: null,
            label: "Upload Image",
        });
        await flushPromises();

        expect(wrapper.find(".image-preview").exists()).toBe(false);
    });

    it("shows thumbnail when file is selected (using object URL)", async () => {
        const file = new File(["test"], "test.png", { type: "image/png" });

        const wrapper = mountComponent({
            modelValue: file,
            label: "Upload Image",
        });
        await flushPromises();

        const preview = wrapper.find(".image-preview");
        expect(preview.exists()).toBe(true);

        expect(URL.createObjectURL).toHaveBeenCalledWith(file);
    });

    it("prefers newly selected file over existing URL", async () => {
        const file = new File(["test"], "new.png", { type: "image/png" });

        const wrapper = mountComponent({
            modelValue: file,
            label: "Upload Image",
            currentImageUrl: "https://example.com/old.jpg",
        });
        await flushPromises();

        // Find the VImg inside the preview
        const img = wrapper.find(".image-preview").findComponent({ name: "VImg" });
        // Should use the object URL from the file, not the current URL
        expect(img.props("src")).toBe("blob:test-0");
    });

    // Note: Dialog opening tests are skipped because VDialog requires visualViewport
    // which is not available in the happy-dom test environment. The dialog functionality
    // is tested via e2e tests or manual testing.

    it("emits update:modelValue when file input changes", async () => {
        const wrapper = mountComponent({
            modelValue: null,
            label: "Upload Image",
        });
        await flushPromises();

        const file = new File(["test"], "test.png", { type: "image/png" });

        // Simulate file input update
        const fileInput = wrapper.findComponent({ name: "VFileInput" });
        await fileInput.vm.$emit("update:modelValue", file);

        expect(wrapper.emitted("update:modelValue")).toBeTruthy();
        expect(wrapper.emitted("update:modelValue")![0]).toEqual([file]);
    });

    it("shows error message when provided", async () => {
        const wrapper = mountComponent({
            modelValue: null,
            label: "Upload Image",
            errorMessage: "File is required",
        });
        await flushPromises();

        const fileInput = wrapper.findComponent({ name: "VFileInput" });
        expect(fileInput.props("errorMessages")).toBe("File is required");
    });

    it("uses custom accept attribute", async () => {
        const wrapper = mountComponent({
            modelValue: null,
            label: "Upload Image",
            accept: "image/png,image/jpeg",
        });
        await flushPromises();

        // Find the actual input element
        const input = wrapper.find('input[type="file"]');
        expect(input.attributes("accept")).toBe("image/png,image/jpeg");
    });

    it("uses default accept attribute for images", async () => {
        const wrapper = mountComponent({
            modelValue: null,
            label: "Upload Image",
        });
        await flushPromises();

        const input = wrapper.find('input[type="file"]');
        expect(input.attributes("accept")).toBe("image/*");
    });

    it("revokes object URL when file changes", async () => {
        const file1 = new File(["test1"], "test1.png", { type: "image/png" });
        const file2 = new File(["test2"], "test2.png", { type: "image/png" });

        const wrapper = mountComponent({
            modelValue: file1,
            label: "Upload Image",
        });
        await flushPromises();
        expect(createdObjectUrls.length).toBe(1);

        // Change the file
        await wrapper.setProps({ modelValue: file2 });
        await flushPromises();

        // Should have revoked the first URL
        expect(revokedObjectUrls.length).toBe(1);
        expect(revokedObjectUrls[0]).toBe(createdObjectUrls[0]);

        // Should have created a new URL
        expect(createdObjectUrls.length).toBe(2);
    });

    it("revokes object URL on unmount", async () => {
        const file = new File(["test"], "test.png", { type: "image/png" });

        const wrapper = mountComponent({
            modelValue: file,
            label: "Upload Image",
        });
        await flushPromises();
        expect(createdObjectUrls.length).toBe(1);

        wrapper.unmount();

        expect(revokedObjectUrls.length).toBe(1);
        expect(revokedObjectUrls[0]).toBe(createdObjectUrls[0]);
    });

    it("handles clearing file selection", async () => {
        const file = new File(["test"], "test.png", { type: "image/png" });

        const wrapper = mountComponent({
            modelValue: file,
            label: "Upload Image",
        });
        await flushPromises();
        expect(wrapper.find(".image-preview").exists()).toBe(true);

        // Clear the file
        await wrapper.setProps({ modelValue: null });
        await flushPromises();

        // Should revoke the URL
        expect(revokedObjectUrls.length).toBe(1);

        // Without currentImageUrl, preview should not be visible
        expect(wrapper.find(".image-preview").exists()).toBe(false);
    });

    it("falls back to currentImageUrl when file is cleared", async () => {
        const file = new File(["test"], "test.png", { type: "image/png" });

        const wrapper = mountComponent({
            modelValue: file,
            label: "Upload Image",
            currentImageUrl: "https://example.com/fallback.jpg",
        });
        await flushPromises();

        // Should show object URL
        let img = wrapper.find(".image-preview").findComponent({ name: "VImg" });
        expect(img.props("src")).toBe("blob:test-0");

        // Clear the file
        await wrapper.setProps({ modelValue: null });
        await flushPromises();

        // Should fall back to currentImageUrl
        img = wrapper.find(".image-preview").findComponent({ name: "VImg" });
        expect(img.props("src")).toBe("https://example.com/fallback.jpg");
    });

    it("has proper accessibility attributes on preview button", async () => {
        const wrapper = mountComponent({
            modelValue: null,
            label: "Upload Image",
            currentImageUrl: "https://example.com/image.jpg",
        });
        await flushPromises();

        const preview = wrapper.find(".image-preview");
        expect(preview.attributes("role")).toBe("button");
        expect(preview.attributes("tabindex")).toBe("0");
        expect(preview.attributes("title")).toBeTruthy();
    });

    it("emits null when clear button is clicked", async () => {
        const wrapper = mountComponent({
            modelValue: null,
            label: "Upload Image",
            currentImageUrl: "https://example.com/image.jpg",
        });
        await flushPromises();

        // Simulate clear button click
        const fileInput = wrapper.findComponent({ name: "VFileInput" });
        await fileInput.vm.$emit("click:clear");

        expect(wrapper.emitted("update:modelValue")).toBeTruthy();
        expect(wrapper.emitted("update:modelValue")![0]).toEqual([null]);
    });

    it("hides preview after clearing via clear button", async () => {
        const wrapper = mountComponent({
            modelValue: null,
            label: "Upload Image",
            currentImageUrl: "https://example.com/image.jpg",
        });
        await flushPromises();

        expect(wrapper.find(".image-preview").exists()).toBe(true);

        // Simulate clear button click
        const fileInput = wrapper.findComponent({ name: "VFileInput" });
        await fileInput.vm.$emit("click:clear");
        await flushPromises();

        expect(wrapper.find(".image-preview").exists()).toBe(false);
    });
});
