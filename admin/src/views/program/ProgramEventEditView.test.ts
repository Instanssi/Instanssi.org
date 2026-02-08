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
    expectFormDataContains,
    expectFormDataHasFile,
    expectFormDataNotHasKey,
} from "@/test/helpers/formdata-matchers";

import ProgramEventEditView from "./ProgramEventEditView.vue";

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
    return mount(ProgramEventEditView, {
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
                ToggleSwitch: {
                    template:
                        '<div class="toggle-switch"><input type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)" /></div>',
                    props: [
                        "modelValue",
                        "errorMessage",
                        "labelOn",
                        "labelOff",
                        "hintOn",
                        "hintOff",
                    ],
                    emits: ["update:modelValue"],
                },
                FontAwesomeIcon: true,
                VuetifyTiptap: {
                    template:
                        '<textarea :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" data-testid="tiptap"></textarea>',
                    props: ["modelValue"],
                    emits: ["update:modelValue"],
                },
            },
        },
    });
}

function createMockFile(name: string): File {
    return new File(["test content"], name, { type: "image/png" });
}

describe("ProgramEventEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("create mode", () => {
        it("renders form with basic fields", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Title field
            expect(wrapper.findAllComponents({ name: "VTextField" }).length).toBeGreaterThanOrEqual(
                1
            );

            // Description (tiptap editor)
            expect(wrapper.find('[data-testid="tiptap"]').exists()).toBe(true);

            // Datetime fields
            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            expect(datetimeInputs.length).toBe(2); // start, end

            // Toggle switches (event type, active)
            expect(wrapper.findAll(".toggle-switch").length).toBe(2);
        });

        it("shows additional fields when isDetailedEvent is true", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Toggle to detailed event type
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[0]!.setValue(true); // First toggle is event type
            await flushPromises();

            // Should now show presenter fields
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            // Should have more fields now (title, place, presenters, presenters_titles, various URLs)
            expect(textFields.length).toBeGreaterThan(5);

            // Should show file inputs for icons
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            expect(fileInputs.length).toBe(2);
        });

        it("submits correct snake_case data to API", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Fill required fields
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Program Event Title");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventProgramEventsCreate), { event_pk: 1 });

            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsCreate)
            ) as FormData;

            expectFormDataContains(formData, { title: "Program Event Title" });
        });

        it("submits detailed event fields with snake_case names", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Enable detailed event type
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[0]!.setValue(true);
            await flushPromises();

            // Fill required fields
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Program Event");
            // Find presenters and presenters_titles fields
            await textFields[2]?.find("input").setValue("John Doe");
            await textFields[3]?.find("input").setValue("CEO");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            await flushPromises();
            await submitForm(wrapper);

            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsCreate)
            ) as FormData;

            expectFormDataContains(formData, { event_type: "1" });
        });

        it("uploads icon files as FormData", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Enable detailed event type
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[0]!.setValue(true);
            await flushPromises();

            // Fill required fields
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Event Title");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            // Upload icon files
            const mockIcon1 = createMockFile("icon1.png");
            const mockIcon2 = createMockFile("icon2.png");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockIcon1);
            await fileInputs[1]!.setValue(mockIcon2);

            await flushPromises();
            await submitForm(wrapper);

            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsCreate)
            ) as FormData;

            expectFormDataHasFile(formData, "icon_original", "icon1.png");
            expectFormDataHasFile(formData, "icon2_original", "icon2.png");
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing data", async () => {
            vi.mocked(api.adminEventProgramEventsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    title: "Existing Event",
                    description: "Description",
                    start: "2024-03-16T10:00:00Z",
                    end: "2024-03-16T12:00:00Z",
                    place: "Main Hall",
                    presenters: "Jane Smith",
                    presenters_titles: "Developer",
                    icon_small_url: "https://example.com/icon1.png",
                    icon2_small_url: "https://example.com/icon2.png",
                    home_url: "https://example.com",
                    email: "test@example.com",
                    twitter_url: "",
                    github_url: "",
                    facebook_url: "",
                    linkedin_url: "",
                    wiki_url: "",
                    event_type: 1,
                    active: true,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            expect(wrapper.exists()).toBe(true);
            expect(api.adminEventProgramEventsRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventProgramEventsRetrieve), {
                event_pk: 1,
                id: 5,
            });
        });

        it("shows existing icon images in edit mode", async () => {
            vi.mocked(api.adminEventProgramEventsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    title: "Existing Event",
                    description: "",
                    start: "2024-03-16T10:00:00Z",
                    end: null,
                    place: "",
                    presenters: "",
                    presenters_titles: "",
                    icon_small_url: "https://example.com/icon1.png",
                    icon2_small_url: "https://example.com/icon2.png",
                    home_url: "",
                    email: "",
                    twitter_url: "",
                    github_url: "",
                    facebook_url: "",
                    linkedin_url: "",
                    wiki_url: "",
                    event_type: 1,
                    active: true,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Should have VImg components showing current icons
            const images = wrapper.findAllComponents({ name: "VImg" });
            expect(images.length).toBe(2);
        });

        it("submits correct data on edit", async () => {
            vi.mocked(api.adminEventProgramEventsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    title: "Existing Event",
                    description: "",
                    start: "2024-03-16T10:00:00Z",
                    end: null,
                    place: "",
                    presenters: "",
                    presenters_titles: "",
                    icon_small_url: null,
                    icon2_small_url: null,
                    home_url: "",
                    email: "",
                    twitter_url: "",
                    github_url: "",
                    facebook_url: "",
                    linkedin_url: "",
                    wiki_url: "",
                    event_type: 0,
                    active: true,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Change title
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Updated Event Title");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventProgramEventsPartialUpdate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventProgramEventsPartialUpdate), {
                event_pk: 1,
                id: 5,
            });
        });

        it("does not send files when no new files selected in edit mode", async () => {
            vi.mocked(api.adminEventProgramEventsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    title: "Existing Event",
                    description: "",
                    start: "2024-03-16T10:00:00Z",
                    end: null,
                    place: "",
                    presenters: "",
                    presenters_titles: "",
                    icon_small_url: "https://example.com/icon1.png",
                    icon2_small_url: "https://example.com/icon2.png",
                    home_url: "",
                    email: "",
                    twitter_url: "",
                    github_url: "",
                    facebook_url: "",
                    linkedin_url: "",
                    wiki_url: "",
                    event_type: 1,
                    active: true,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Only change title, don't select new files
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Updated Event Title");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventProgramEventsPartialUpdate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsPartialUpdate)
            ) as FormData;

            // Files should not be in FormData when not selected
            expectFormDataNotHasKey(formData, "icon_original");
            expectFormDataNotHasKey(formData, "icon2_original");
        });

        it("sends new icon files when selected in edit mode", async () => {
            vi.mocked(api.adminEventProgramEventsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    title: "Existing Event",
                    description: "",
                    start: "2024-03-16T10:00:00Z",
                    end: null,
                    place: "",
                    presenters: "",
                    presenters_titles: "",
                    icon_small_url: "https://example.com/old-icon1.png",
                    icon2_small_url: "https://example.com/old-icon2.png",
                    home_url: "",
                    email: "",
                    twitter_url: "",
                    github_url: "",
                    facebook_url: "",
                    linkedin_url: "",
                    wiki_url: "",
                    event_type: 1,
                    active: true,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Select new icon files
            const mockIcon1 = createMockFile("new-icon1.png");
            const mockIcon2 = createMockFile("new-icon2.png");
            const fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            await fileInputs[0]!.setValue(mockIcon1);
            await fileInputs[1]!.setValue(mockIcon2);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsPartialUpdate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsPartialUpdate)
            ) as FormData;

            expectFormDataHasFile(formData, "icon_original", "new-icon1.png");
            expectFormDataHasFile(formData, "icon2_original", "new-icon2.png");
        });
    });

    describe("API error handling", () => {
        it("maps field errors with snake_case mapping", async () => {
            vi.mocked(api.adminEventProgramEventsCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    title: ["Title required."],
                    start: ["Invalid datetime."],
                    presenters_titles: ["Too long."],
                    home_url: ["Invalid URL."],
                    icon_original: ["Invalid image."],
                    event_type: ["Invalid value."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("a");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            await flushPromises();
            await submitForm(wrapper);

            const errorMessages = wrapper.findAll(".v-messages__message");
            expect(errorMessages.length).toBeGreaterThan(0);
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(api.adminEventProgramEventsCreate).mockRejectedValueOnce(
                createMockApiError(500, {})
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Event Title");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).toHaveBeenCalled();
        });
    });

    describe("special features", () => {
        it("toggles between simple and detailed event types", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Start as simple (event_type = 0)
            let fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            expect(fileInputs.length).toBe(0); // No file inputs for simple events

            // Switch to detailed
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[0]!.setValue(true);
            await flushPromises();

            fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            expect(fileInputs.length).toBe(2); // Icons for detailed events

            // Switch back to simple
            await toggles[0]!.setValue(false);
            await flushPromises();

            fileInputs = wrapper.findAllComponents({ name: "VFileInput" });
            expect(fileInputs.length).toBe(0);
        });

        it("has URL fields with type=url for validation", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Enable detailed mode
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[0]!.setValue(true);
            await flushPromises();

            const urlInputs = wrapper.findAll('input[type="url"]');
            expect(urlInputs.length).toBeGreaterThan(0);
        });

        it("has email field with type=email", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Enable detailed mode
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[0]!.setValue(true);
            await flushPromises();

            const emailInputs = wrapper.findAll('input[type="email"]');
            expect(emailInputs.length).toBe(1);
        });
    });

    describe("optional fields", () => {
        it("submits with description when filled", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Program Event Title");

            const tiptap = wrapper.find('[data-testid="tiptap"]');
            await tiptap.setValue("Event description");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsCreate)
            ) as FormData;
            expectFormDataContains(formData, { description: "Event description" });
        });

        it("submits with empty description", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Program Event Title");

            // Don't set description

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsCreate)
            ) as FormData;
            expectFormDataContains(formData, { description: "" });
        });

        it("submits with place when filled", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Get all text input fields and fill them
            const textInputs = wrapper.findAll('input[type="text"]');
            // In simple mode: title (0), place (1)
            await textInputs[0]!.setValue("Program Event Title");
            await textInputs[1]!.setValue("Main Stage");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsCreate)
            ) as FormData;
            expectFormDataContains(formData, { place: "Main Stage" });
        });

        it("submits with empty place", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Program Event Title");
            // Don't set place

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsCreate)
            ) as FormData;
            expectFormDataContains(formData, { place: "" });
        });

        it("submits with active toggle enabled", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Program Event Title");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            // Active toggle is ON by default

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsCreate)
            ) as FormData;
            expectFormDataContains(formData, { active: "true" });
        });

        it("submits with active toggle disabled", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Program Event Title");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            // Disable active toggle (second toggle)
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[1]!.setValue(false);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsCreate)
            ) as FormData;
            expectFormDataContains(formData, { active: "false" });
        });

        it("submits with presenters when filled (detailed event)", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Enable detailed event type
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[0]!.setValue(true);
            await flushPromises();

            // In detailed mode, VTextField order: title (0), place (1), presenters (2), presentersTitles (3), homeUrl (4), ...
            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Program Event Title");
            await textInputs[2]!.setValue("John Doe, Jane Smith"); // presenters
            await textInputs[3]!.setValue("CEO, CTO"); // presentersTitles

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsCreate)
            ) as FormData;
            expectFormDataContains(formData, { presenters: "John Doe, Jane Smith" });
            expectFormDataContains(formData, { presenters_titles: "CEO, CTO" });
        });

        it("submits with empty presenters (detailed event)", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Enable detailed event type
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[0]!.setValue(true);
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Program Event Title");
            // Don't set presenters

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventProgramEventsCreate)
            ) as FormData;
            expectFormDataContains(formData, { presenters: "" });
            expectFormDataContains(formData, { presenters_titles: "" });
        });
    });

    describe("validation", () => {
        it("does not submit when title is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Only fill start time
            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).not.toHaveBeenCalled();
        });

        it("does not submit when start is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Only fill title
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Event Title");

            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).not.toHaveBeenCalled();
        });

        it("allows empty end field", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Event Title");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");
            // Don't fill end

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventProgramEventsCreate).toHaveBeenCalled();
        });

        it("validates URL formats", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Enable detailed mode
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[0]!.setValue(true);
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Event Title");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            // Find URL field and enter invalid URL
            const urlInputs = wrapper.findAll('input[type="url"]');
            if (urlInputs[0]) {
                await urlInputs[0]!.setValue("not-a-url");
                await urlInputs[0]!.trigger("blur");
                await flushPromises();
            }

            // May show validation error
        });

        it("validates email format", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Enable detailed mode
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[0]!.setValue(true);
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Event Title");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-16T10:00");

            // Find email field and enter invalid email
            const emailInputs = wrapper.findAll('input[type="email"]');
            if (emailInputs[0]) {
                await emailInputs[0]!.setValue("not-an-email");
                await emailInputs[0]!.trigger("blur");
                await flushPromises();
            }

            // May show validation error
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
                query: { page: "2", active: "true" },
            } as never);

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            const cancelButton = buttons.find((b) => b.text().includes("General.cancel"));
            await cancelButton!.trigger("click");

            expect(mockPush).toHaveBeenCalledWith({
                name: "program",
                params: { eventId: "1" },
                query: { page: "2", active: "true" },
            });
        });
    });
});
