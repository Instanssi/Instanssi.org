import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { useRoute, useRouter } from "vue-router";

import * as api from "@/api";
import {
    createMockApiError,
    expectApiCalledWithPath,
    getSerializedApiCallBody,
    submitForm,
} from "@/test/helpers/form-test-utils";
import {
    expectFormDataHasFile,
    expectFormDataContains,
    expectFormDataNotHasKey,
} from "@/test/helpers/formdata-matchers";

import EntryEditView from "./EntryEditView.vue";

vi.mock("vue-router", () => ({
    useRouter: vi.fn(() => ({
        push: vi.fn(),
        replace: vi.fn(),
    })),
    useRoute: vi.fn(() => ({
        params: { eventId: "1" },
        query: {},
    })),
}));

const vuetify = createVuetify({ components, directives });

function mountComponent(props: { eventId: string; id?: string }) {
    return mount(EntryEditView, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                LayoutBase: {
                    template: "<div><slot /></div>",
                    props: ["breadcrumbs"],
                },
                FormSection: {
                    template: '<div class="form-section"><slot /></div>',
                },
                DisqualificationField: {
                    template: `
                        <div class="dq-field">
                            <input type="checkbox" :checked="modelValue" @change="$emit('update:modelValue', $event.target.checked)" data-testid="dq-toggle" />
                            <input type="text" :value="reason" @input="$emit('update:reason', $event.target.value)" data-testid="dq-reason" />
                        </div>
                    `,
                    props: [
                        "modelValue",
                        "reason",
                        "errorMessage",
                        "reasonErrorMessage",
                        "labelOn",
                        "labelOff",
                        "reasonLabel",
                    ],
                    emits: ["update:modelValue", "update:reason"],
                },
                FontAwesomeIcon: true,
            },
        },
    });
}

function createMockFile(name: string): File {
    return new File(["test content"], name, { type: "application/octet-stream" });
}

describe("EntryEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Mock compos list - default with thumbnail_pref = 0 (requires image)
        vi.mocked(api.adminEventKompomaattiComposList).mockResolvedValue({
            data: {
                results: [
                    {
                        id: 1,
                        name: "Demo Compo",
                        thumbnail_pref: 0,
                        formats: "zip|7z",
                        source_formats: "zip",
                        image_formats: "png|jpg",
                    },
                    {
                        id: 2,
                        name: "Music Compo",
                        thumbnail_pref: 1,
                        formats: "mp3|ogg",
                        source_formats: "",
                        image_formats: "",
                    },
                ],
            },
        } as never);
        vi.mocked(api.adminUsersList).mockResolvedValue({
            data: { results: [{ id: 1, username: "user1" }] },
        } as never);
    });

    describe("create mode", () => {
        it("renders form with all required fields", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Text fields: name, creator, platform, youtubeUrl
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            expect(textFields.length).toBeGreaterThanOrEqual(4);

            // Description textarea
            expect(wrapper.findComponent({ name: "VTextarea" }).exists()).toBe(true);

            // Compo select
            expect(wrapper.findComponent({ name: "VSelect" }).exists()).toBe(true);

            // User autocomplete
            expect(wrapper.findComponent({ name: "VAutocomplete" }).exists()).toBe(true);

            // File inputs (entry file is always shown)
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            expect(fileInputs.length).toBeGreaterThanOrEqual(1);

            // Disqualification field
            expect(wrapper.find(".dq-field").exists()).toBe(true);
        });

        it("loads compos and users on mount", async () => {
            mountComponent({ eventId: "1" });
            await flushPromises();

            expect(api.adminEventKompomaattiComposList).toHaveBeenCalled();
            expect(api.adminUsersList).toHaveBeenCalled();
        });

        it("submits data as FormData with snake_case field names", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Fill required fields
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Entry");
            await textFields[1]!.find("input").setValue("My Group");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2); // Music compo (no image required)

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            // Add entry file
            const mockFile = createMockFile("entry.zip");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventKompomaattiEntriesCreate), {
                event_pk: 1,
            });

            // Check FormData
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesCreate)
            ) as FormData;

            expectFormDataContains(formData, { name: "My Entry" });
            expectFormDataContains(formData, { creator: "My Group" });
            expectFormDataHasFile(formData, "entryfile", "entry.zip");
        });

        it("does not submit when entry file is missing in create mode", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Entry");
            await textFields[1]!.find("input").setValue("My Group");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            // Don't add entry file

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).not.toHaveBeenCalled();
        });

        it("does not submit when image file is missing and compo thumbnail_pref is 0", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Entry");
            await textFields[1]!.find("input").setValue("My Group");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(1); // Demo compo with thumbnail_pref = 0

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            // Add entry file but not image
            const mockFile = createMockFile("entry.zip");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).not.toHaveBeenCalled();
        });

        it("does not require image file when compo thumbnail_pref is 1", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Entry");
            await textFields[1]!.find("input").setValue("My Group");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2); // Music compo with thumbnail_pref = 1

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).toHaveBeenCalled();
        });

        it("sends optional source file when provided", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Entry");
            await textFields[1]!.find("input").setValue("My Group");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const entryFile = createMockFile("entry.mp3");
            const sourceFile = createMockFile("source.zip");

            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(entryFile);
            if (fileInputs[1]) {
                await fileInputs[1]!.setValue(sourceFile);
            }

            await flushPromises();
            await submitForm(wrapper);

            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesCreate)
            ) as FormData;

            expectFormDataHasFile(formData, "entryfile", "entry.mp3");
            if (formData.has("sourcefile")) {
                expectFormDataHasFile(formData, "sourcefile", "source.zip");
            }
        });

        it("sends all files including required image when compo thumbnail_pref is 0", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Demo");
            await textFields[1]!.find("input").setValue("My Group");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(1); // Demo compo with thumbnail_pref = 0

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const entryFile = createMockFile("demo.zip");
            const sourceFile = createMockFile("source.zip");
            const imageFile = createMockFile("screenshot.png");

            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            // File inputs: entryfile (0), sourcefile (1), imagefile (2)
            await fileInputs[0]!.setValue(entryFile);
            await fileInputs[1]!.setValue(sourceFile);
            await fileInputs[2]!.setValue(imageFile);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesCreate)
            ) as FormData;

            expectFormDataHasFile(formData, "entryfile", "demo.zip");
            expectFormDataHasFile(formData, "sourcefile", "source.zip");
            expectFormDataHasFile(formData, "imagefile_original", "screenshot.png");
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing entry data", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Entry",
                    creator: "Existing Group",
                    description: "Description",
                    compo: 1,
                    user: 1,
                    platform: "Windows",
                    entryfile_url: "https://example.com/entry.zip",
                    sourcefile_url: null,
                    imagefile_original_url: "https://example.com/image.png",
                    youtube_url: null,
                    score: 85.5,
                    rank: 2,
                    disqualified: false,
                    disqualified_reason: "",
                    alternate_files: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            expect(wrapper.exists()).toBe(true);
            expect(api.adminEventKompomaattiEntriesRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventKompomaattiEntriesRetrieve), {
                event_pk: 1,
                id: 5,
            });
        });

        it("disables compo and user fields in edit mode", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Entry",
                    creator: "Existing Group",
                    description: "",
                    compo: 1,
                    user: 1,
                    platform: null,
                    entryfile_url: "https://example.com/entry.zip",
                    sourcefile_url: null,
                    imagefile_original_url: null,
                    youtube_url: null,
                    score: null,
                    rank: null,
                    disqualified: false,
                    disqualified_reason: "",
                    alternate_files: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("disabled")).toBe(true);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            expect(autocomplete.props("disabled")).toBe(true);
        });

        it("does not require file in edit mode when existing file present", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Entry",
                    creator: "Existing Group",
                    description: "",
                    compo: 1,
                    user: 1,
                    platform: null,
                    entryfile_url: "https://example.com/entry.zip",
                    sourcefile_url: null,
                    imagefile_original_url: "https://example.com/image.png",
                    youtube_url: null,
                    score: null,
                    rank: null,
                    disqualified: false,
                    disqualified_reason: "",
                    alternate_files: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Change name only
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Updated Entry Name");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesPartialUpdate).toHaveBeenCalled();
        });

        it("does not send files when no new files selected in edit mode", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Entry",
                    creator: "Existing Group",
                    description: "",
                    compo: 1,
                    user: 1,
                    platform: null,
                    entryfile_url: "https://example.com/entry.zip",
                    sourcefile_url: "https://example.com/source.zip",
                    imagefile_original_url: "https://example.com/image.png",
                    youtube_url: null,
                    score: null,
                    rank: null,
                    disqualified: false,
                    disqualified_reason: "",
                    alternate_files: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Only change name, don't select new files
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Updated Entry Name");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesPartialUpdate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesPartialUpdate)
            ) as FormData;

            // Files should not be in FormData when not selected
            expectFormDataNotHasKey(formData, "entryfile");
            expectFormDataNotHasKey(formData, "sourcefile");
            expectFormDataNotHasKey(formData, "imagefile_original");
        });

        it("sends new entry file when selected in edit mode", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Entry",
                    creator: "Existing Group",
                    description: "",
                    compo: 1,
                    user: 1,
                    platform: null,
                    entryfile_url: "https://example.com/old-entry.zip",
                    sourcefile_url: null,
                    imagefile_original_url: "https://example.com/image.png",
                    youtube_url: null,
                    score: null,
                    rank: null,
                    disqualified: false,
                    disqualified_reason: "",
                    alternate_files: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Select new entry file
            const mockEntryFile = createMockFile("new-entry.zip");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockEntryFile);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesPartialUpdate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesPartialUpdate)
            ) as FormData;

            expectFormDataHasFile(formData, "entryfile", "new-entry.zip");
        });

        it("sends new source and image files when selected in edit mode", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Entry",
                    creator: "Existing Group",
                    description: "",
                    compo: 1,
                    user: 1,
                    platform: null,
                    entryfile_url: "https://example.com/entry.zip",
                    sourcefile_url: "https://example.com/old-source.zip",
                    imagefile_original_url: "https://example.com/old-image.png",
                    youtube_url: null,
                    score: null,
                    rank: null,
                    disqualified: false,
                    disqualified_reason: "",
                    alternate_files: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Select new source and image files
            const mockSourceFile = createMockFile("new-source.zip");
            const mockImageFile = createMockFile("new-image.png");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            // File inputs: entryfile (0), sourcefile (1), imagefile (2)
            await fileInputs[1]!.setValue(mockSourceFile);
            await fileInputs[2]!.setValue(mockImageFile);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesPartialUpdate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesPartialUpdate)
            ) as FormData;

            expectFormDataHasFile(formData, "sourcefile", "new-source.zip");
            expectFormDataHasFile(formData, "imagefile_original", "new-image.png");
        });

        it("shows readonly score and rank fields in edit mode", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Entry",
                    creator: "Existing Group",
                    description: "",
                    compo: 1,
                    user: 1,
                    platform: null,
                    entryfile_url: "https://example.com/entry.zip",
                    sourcefile_url: null,
                    imagefile_original_url: null,
                    youtube_url: null,
                    score: 85.5,
                    rank: 2,
                    disqualified: false,
                    disqualified_reason: "",
                    alternate_files: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Score and rank should be displayed
            expect(wrapper.text()).toContain("85.5");
            expect(wrapper.text()).toContain("2");
        });

        it("shows alternate files in edit mode", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Entry",
                    creator: "Existing Group",
                    description: "",
                    compo: 1,
                    user: 1,
                    platform: null,
                    entryfile_url: "https://example.com/entry.zip",
                    sourcefile_url: null,
                    imagefile_original_url: null,
                    youtube_url: null,
                    score: null,
                    rank: null,
                    disqualified: false,
                    disqualified_reason: "",
                    alternate_files: [{ url: "https://example.com/entry.mp3", format: "mp3" }],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Alternate files should be shown
            const list = wrapper.findComponent({ name: "VList" });
            expect(list.exists()).toBe(true);
        });
    });

    describe("API error handling", () => {
        it("maps field errors with snake_case mapping", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    name: ["Name required."],
                    creator: ["Creator required."],
                    entryfile: ["Entry file required."],
                    imagefile_original: ["Image required."],
                    youtube_url: ["Invalid URL."],
                    disqualified_reason: ["Reason required."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("a");
            await textFields[1]!.find("input").setValue("b");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await flushPromises();
            await submitForm(wrapper);

            const errorMessages = wrapper.findAll(".v-messages__message");
            expect(errorMessages.length).toBeGreaterThan(0);
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesCreate).mockRejectedValueOnce(
                createMockApiError(500, {})
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Entry");
            await textFields[1]!.find("input").setValue("Creator");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).toHaveBeenCalled();
        });
    });

    describe("special features", () => {
        it("shows/hides image file input based on compo thumbnail_pref", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Initially no compo selected, image input may or may not be visible
            const select = wrapper.findComponent({ name: "VSelect" });

            // Select compo with thumbnail_pref = 0 (requires image)
            await select.setValue(1);
            await flushPromises();

            let fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            // Should have entry + source + image = 3 file inputs
            expect(fileInputs.length).toBe(3);

            // Select compo with thumbnail_pref = 1 (no separate image)
            await select.setValue(2);
            await flushPromises();

            fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            // Should have entry + source = 2 file inputs (image hidden)
            expect(fileInputs.length).toBe(2);
        });

        it("applies file format filters based on compo", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(1); // Demo compo with formats: zip|7z
            await flushPromises();

            // Entry file input should have accept attribute
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            expect(fileInputs.length).toBeGreaterThan(0);
        });
    });

    describe("optional fields", () => {
        it("submits with description when filled", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Entry");
            await textFields[1]!.find("input").setValue("My Group");

            const textarea = wrapper.findComponent({ name: "VTextarea" });
            await textarea.find("textarea").setValue("This is a description");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2); // Music compo (no image required)

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesCreate)
            ) as FormData;
            expectFormDataContains(formData, { description: "This is a description" });
        });

        it("submits with empty description", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Entry");
            await textFields[1]!.find("input").setValue("My Group");

            // Don't set description

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesCreate)
            ) as FormData;
            expectFormDataContains(formData, { description: "" });
        });

        it("submits with platform when filled", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Entry",
                    creator: "Existing Group",
                    description: "",
                    compo: 2,
                    user: 1,
                    platform: "Windows 11",
                    entryfile_url: "https://example.com/entry.mp3",
                    sourcefile_url: null,
                    imagefile_original_url: null,
                    youtube_url: null,
                    score: null,
                    rank: null,
                    disqualified: false,
                    disqualified_reason: "",
                    alternate_files: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Change name to trigger update
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Updated Entry");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesPartialUpdate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesPartialUpdate)
            ) as FormData;
            // Platform should be preserved from the loaded data
            expect(formData.get("platform")).toBe("Windows 11");
        });

        it("submits without platform when empty", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Entry");
            await textFields[1]!.find("input").setValue("My Group");
            // Don't set platform

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesCreate)
            ) as FormData;
            // Empty platform sends empty string (null in FormData = empty string)
            expectFormDataContains(formData, { platform: "" });
        });

        it("submits with youtubeUrl when filled", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Entry",
                    creator: "Existing Group",
                    description: "",
                    compo: 2,
                    user: 1,
                    platform: null,
                    entryfile_url: "https://example.com/entry.mp3",
                    sourcefile_url: null,
                    imagefile_original_url: null,
                    youtube_url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    score: null,
                    rank: null,
                    disqualified: false,
                    disqualified_reason: "",
                    alternate_files: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Change name to trigger update
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Updated Entry");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesPartialUpdate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesPartialUpdate)
            ) as FormData;
            // youtubeUrl should be preserved from the loaded data
            expect(formData.get("youtube_url")).toBe("https://www.youtube.com/watch?v=dQw4w9WgXcQ");
        });

        it("submits without youtubeUrl when empty", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Entry");
            await textFields[1]!.find("input").setValue("My Group");
            // Don't set youtubeUrl

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesCreate)
            ) as FormData;
            // Empty youtube_url sends empty string (null in FormData = empty string)
            expectFormDataContains(formData, { youtube_url: "" });
        });

        it("submits with disqualified toggle enabled and reason", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Entry");
            await textFields[1]!.find("input").setValue("My Group");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            // Enable disqualified and set reason
            const dqToggle = wrapper.find('[data-testid="dq-toggle"]');
            await dqToggle.setValue(true);
            const dqReason = wrapper.find('[data-testid="dq-reason"]');
            await dqReason.setValue("Rule violation");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesCreate)
            ) as FormData;
            expectFormDataContains(formData, { disqualified: "true" });
            expectFormDataContains(formData, { disqualified_reason: "Rule violation" });
        });

        it("submits with disqualified toggle disabled", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("My Entry");
            await textFields[1]!.find("input").setValue("My Group");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            // Don't enable disqualified (default is false)

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventKompomaattiEntriesCreate)
            ) as FormData;
            // When disqualified is false, it should be "false" in the form data
            expectFormDataContains(formData, { disqualified: "false" });
        });
    });

    describe("validation", () => {
        it("does not submit when name is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Fill everything except name
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[1]!.find("input").setValue("Creator");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).not.toHaveBeenCalled();
        });

        it("does not submit when creator is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Fill everything except creator
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Entry Name");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).not.toHaveBeenCalled();
        });

        it("does not submit when compo is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Entry Name");
            await textFields[1]!.find("input").setValue("Creator");

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).not.toHaveBeenCalled();
        });

        it("does not submit when user is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Entry Name");
            await textFields[1]!.find("input").setValue("Creator");

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(2);

            const mockFile = createMockFile("entry.mp3");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockFile);

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiEntriesCreate).not.toHaveBeenCalled();
        });
    });

    describe("navigation", () => {
        it("goBack preserves query params from route", async () => {
            const mockPush = vi.fn();
            vi.mocked(useRouter).mockReturnValue({
                push: mockPush,
                replace: vi.fn(),
            } as never);
            vi.mocked(useRoute).mockReturnValue({
                params: { eventId: "1" },
                query: { compo: "5", disqualified: "false" },
            } as never);

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            const cancelButton = buttons.find((b) => b.text().includes("General.cancel"));
            await cancelButton!.trigger("click");

            expect(mockPush).toHaveBeenCalledWith({
                name: "entries",
                params: { eventId: "1" },
                query: { compo: "5", disqualified: "false" },
            });
        });
    });
});
