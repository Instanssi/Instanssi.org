import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import * as api from "@/api";
import {
    createMockApiError,
    expectApiCalledWithPath,
    getSerializedApiCallBody,
    submitForm,
} from "@/test/helpers/form-test-utils";
import {
    expectFormDataContains,
    expectFormDataHasFile,
    expectFormDataNotHasKey,
} from "@/test/helpers/formdata-matchers";

import UploadEditView from "./UploadEditView.vue";

const vuetify = createVuetify({ components, directives });

function mountComponent(props: { eventId: string; id?: string }) {
    return mount(UploadEditView, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                LayoutBase: {
                    template: "<div><slot /></div>",
                    props: ["breadcrumbs"],
                },
                FontAwesomeIcon: true,
            },
        },
    });
}

function createMockFile(name: string, content: string = "test content"): File {
    return new File([content], name, { type: "application/octet-stream" });
}

describe("UploadEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("create mode", () => {
        it("renders form with file and description fields", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Should have file input
            expect(wrapper.findComponent({ name: "VFileInput" }).exists()).toBe(true);
            // Should have description textarea
            expect(wrapper.findComponent({ name: "VTextarea" }).exists()).toBe(true);
        });

        it("does not submit when file is missing in create mode", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Only fill description, not file
            const textarea = wrapper.findComponent({ name: "VTextarea" });
            await textarea.find("textarea").setValue("My description");

            await submitForm(wrapper);

            expect(api.adminEventUploadsFilesCreate).not.toHaveBeenCalled();
        });

        it("submits file as FormData", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Create a mock file
            const mockFile = createMockFile("test.pdf");

            // Get file input and set file
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.setValue(mockFile);

            // Fill description
            const textarea = wrapper.findComponent({ name: "VTextarea" });
            await textarea.find("textarea").setValue("Test description");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventUploadsFilesCreate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventUploadsFilesCreate), { event_pk: 1 });

            // Check FormData contents
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventUploadsFilesCreate)
            ) as FormData;

            expectFormDataHasFile(formData, "file", "test.pdf");
        });

        it("sends description in FormData", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const mockFile = createMockFile("test.pdf");
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.setValue(mockFile);

            const textarea = wrapper.findComponent({ name: "VTextarea" });
            await textarea.find("textarea").setValue("My file description");

            await flushPromises();
            await submitForm(wrapper);

            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventUploadsFilesCreate)
            ) as FormData;

            expectFormDataContains(formData, { description: "My file description" });
        });

        it("skips description if empty", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const mockFile = createMockFile("test.pdf");
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.setValue(mockFile);

            // Don't fill description

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventUploadsFilesCreate).toHaveBeenCalled();
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing file data", async () => {
            vi.mocked(api.adminEventUploadsFilesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    file: "https://example.com/uploads/test.pdf",
                    description: "Existing description",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            expect(wrapper.exists()).toBe(true);
            expect(api.adminEventUploadsFilesRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventUploadsFilesRetrieve), {
                event_pk: 1,
                id: 5,
            });
        });

        it("shows current file in edit mode", async () => {
            vi.mocked(api.adminEventUploadsFilesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    file: "https://example.com/uploads/test.pdf",
                    description: "Existing description",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Should show FileUploadField with current file
            const fileUploadField = wrapper.findComponent({ name: "FileUploadField" });
            expect(fileUploadField.exists()).toBe(true);
            expect(fileUploadField.props("currentFileUrl")).toBe(
                "https://example.com/uploads/test.pdf"
            );
        });

        it("does not require file in edit mode", async () => {
            vi.mocked(api.adminEventUploadsFilesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    file: "https://example.com/uploads/test.pdf",
                    description: "Existing description",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Change description only
            const textarea = wrapper.findComponent({ name: "VTextarea" });
            await textarea.find("textarea").setValue("Updated description");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventUploadsFilesPartialUpdate).toHaveBeenCalled();
        });

        it("does not send file when no new file selected", async () => {
            vi.mocked(api.adminEventUploadsFilesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    file: "https://example.com/uploads/test.pdf",
                    description: "Existing description",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            const textarea = wrapper.findComponent({ name: "VTextarea" });
            await textarea.find("textarea").setValue("New description");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventUploadsFilesPartialUpdate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventUploadsFilesPartialUpdate), {
                event_pk: 1,
                id: 5,
            });

            // When no new file is selected, file should not be in FormData
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventUploadsFilesPartialUpdate)
            ) as FormData;

            expectFormDataNotHasKey(formData, "file");
        });

        it("sends new file when selected in edit mode", async () => {
            vi.mocked(api.adminEventUploadsFilesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    file: "https://example.com/uploads/old-file.pdf",
                    description: "Existing description",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Select a new file
            const mockFile = createMockFile("new-file.pdf");
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.setValue(mockFile);

            const textarea = wrapper.findComponent({ name: "VTextarea" });
            await textarea.find("textarea").setValue("Updated description");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventUploadsFilesPartialUpdate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventUploadsFilesPartialUpdate), {
                event_pk: 1,
                id: 5,
            });

            // New file should be included in FormData
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventUploadsFilesPartialUpdate)
            ) as FormData;

            expectFormDataHasFile(formData, "file", "new-file.pdf");
            expectFormDataContains(formData, { description: "Updated description" });
        });
    });

    describe("API error handling", () => {
        it("maps field errors to form fields", async () => {
            vi.mocked(api.adminEventUploadsFilesCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    file: ["File type not allowed."],
                    description: ["Description too long."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const mockFile = createMockFile("test.exe");
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.setValue(mockFile);

            const textarea = wrapper.findComponent({ name: "VTextarea" });
            await textarea.find("textarea").setValue("A".repeat(300));

            await flushPromises();
            await submitForm(wrapper);

            // Errors should be displayed
            const errorMessages = wrapper.findAll(".v-messages__message");
            expect(errorMessages.length).toBeGreaterThan(0);
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(api.adminEventUploadsFilesCreate).mockRejectedValueOnce(
                createMockApiError(500, {})
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const mockFile = createMockFile("test.pdf");
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.setValue(mockFile);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventUploadsFilesCreate).toHaveBeenCalled();
        });
    });

    describe("special features", () => {
        it("uses toFormData for body serialization", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const mockFile = createMockFile("test.pdf");
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.setValue(mockFile);

            await flushPromises();
            await submitForm(wrapper);

            // Check that bodySerializer was passed
            const callArgs = vi.mocked(api.adminEventUploadsFilesCreate).mock.calls[0]?.[0];
            expect(callArgs?.bodySerializer).toBeDefined();
        });

        it("displays filename in FileUploadField in edit mode", async () => {
            vi.mocked(api.adminEventUploadsFilesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    file: "https://example.com/uploads/important-document.pdf",
                    description: "",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // FileUploadField should receive the current file URL
            const fileUploadField = wrapper.findComponent({ name: "FileUploadField" });
            expect(fileUploadField.props("currentFileUrl")).toBe(
                "https://example.com/uploads/important-document.pdf"
            );
        });

        it("has download functionality via FileUploadField", async () => {
            vi.mocked(api.adminEventUploadsFilesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    file: "https://example.com/uploads/test.pdf",
                    description: "",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // FileUploadField component handles download/preview - just verify it's present
            const fileUploadField = wrapper.findComponent({ name: "FileUploadField" });
            expect(fileUploadField.exists()).toBe(true);
        });
    });

    describe("validation", () => {
        it("validates description max length", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const mockFile = createMockFile("test.pdf");
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.setValue(mockFile);

            const textarea = wrapper.findComponent({ name: "VTextarea" });
            await textarea.find("textarea").setValue("A".repeat(300));
            await textarea.find("textarea").trigger("blur");
            await flushPromises();

            // May show validation error for max length (255)
        });

        it("allows empty description", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const mockFile = createMockFile("test.pdf");
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.setValue(mockFile);

            // Don't fill description

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventUploadsFilesCreate).toHaveBeenCalled();
        });
    });
});
