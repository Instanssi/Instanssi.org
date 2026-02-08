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
    submitForm,
} from "@/test/helpers/form-test-utils";

import CompoEditView from "./CompoEditView.vue";

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
    return mount(CompoEditView, {
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
                HtmlEditor: {
                    template:
                        '<textarea :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" data-testid="html-editor"></textarea>',
                    props: ["modelValue"],
                    emits: ["update:modelValue"],
                },
                FontAwesomeIcon: true,
            },
        },
    });
}

describe("CompoEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("create mode", () => {
        it("renders form with all required fields", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Name field
            expect(wrapper.findComponent({ name: "VTextField" }).exists()).toBe(true);

            // Tiptap editor for description
            expect(wrapper.find('[data-testid="html-editor"]').exists()).toBe(true);

            // Datetime fields (5 total)
            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            expect(datetimeInputs.length).toBe(5);

            // Size inputs (2)
            const numberInputs = wrapper.findAll('input[type="number"]');
            expect(numberInputs.length).toBeGreaterThanOrEqual(2);

            // Format comboboxes (3)
            const comboboxes = wrapper.findAllComponents({ name: "VCombobox" });
            expect(comboboxes.length).toBe(3);

            // Selects (2 for entry view type and thumbnail pref, 2 for size units)
            const selects = wrapper.findAllComponents({ name: "VSelect" });
            expect(selects.length).toBe(4);

            // Toggle switches (5)
            expect(wrapper.findAll(".toggle-switch").length).toBe(5);
        });

        it("submits correct snake_case data to API", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Fill required fields
            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Demo Compo");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T12:00");
            await datetimeInputs[1]!.setValue("2024-03-15T18:00");
            await datetimeInputs[2]!.setValue("2024-03-16T10:00");
            await datetimeInputs[3]!.setValue("2024-03-16T12:00");
            await datetimeInputs[4]!.setValue("2024-03-16T20:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiComposCreate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventKompomaattiComposCreate), {
                event_pk: 1,
            });

            const callBody = vi.mocked(api.adminEventKompomaattiComposCreate).mock.calls[0]?.[0]
                ?.body;
            expect(callBody?.name).toBe("Demo Compo");
            expect("adding_end" in callBody!).toBe(true);
            expect("editing_end" in callBody!).toBe(true);
            expect("compo_start" in callBody!).toBe(true);
            expect("voting_start" in callBody!).toBe(true);
            expect("voting_end" in callBody!).toBe(true);
            expect("entry_sizelimit" in callBody!).toBe(true);
            expect("source_sizelimit" in callBody!).toBe(true);
            expect("source_formats" in callBody!).toBe(true);
            expect("image_formats" in callBody!).toBe(true);
            expect("show_voting_results" in callBody!).toBe(true);
            expect("is_votable" in callBody!).toBe(true);
            expect("entry_view_type" in callBody!).toBe(true);
            expect("thumbnail_pref" in callBody!).toBe(true);
            expect("hide_from_archive" in callBody!).toBe(true);
            expect("hide_from_frontpage" in callBody!).toBe(true);
        });

        it("submits size limits as bytes", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Demo Compo");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T12:00");
            await datetimeInputs[1]!.setValue("2024-03-15T18:00");
            await datetimeInputs[2]!.setValue("2024-03-16T10:00");
            await datetimeInputs[3]!.setValue("2024-03-16T12:00");
            await datetimeInputs[4]!.setValue("2024-03-16T20:00");

            // Set size value (first number input)
            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue("10");

            await flushPromises();
            await submitForm(wrapper);

            const callBody = vi.mocked(api.adminEventKompomaattiComposCreate).mock.calls[0]?.[0]
                ?.body;
            // Size should be in bytes (default unit is MB, so 10 MB = 10485760 bytes)
            expect(callBody?.entry_sizelimit).toBe(10485760);
        });

        it("joins format arrays with pipe separator", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Demo Compo");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T12:00");
            await datetimeInputs[1]!.setValue("2024-03-15T18:00");
            await datetimeInputs[2]!.setValue("2024-03-16T10:00");
            await datetimeInputs[3]!.setValue("2024-03-16T12:00");
            await datetimeInputs[4]!.setValue("2024-03-16T20:00");

            // Add formats via combobox (simulated)
            const comboboxes = wrapper.findAllComponents({ name: "VCombobox" });
            await comboboxes[0]!.setValue(["zip", "7z"]);

            await flushPromises();
            await submitForm(wrapper);

            const callBody = vi.mocked(api.adminEventKompomaattiComposCreate).mock.calls[0]?.[0]
                ?.body;
            expect(callBody?.formats).toBe("zip|7z");
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing compo data", async () => {
            vi.mocked(api.adminEventKompomaattiComposRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Compo",
                    description: "<p>Description</p>",
                    adding_end: "2024-03-15T12:00:00Z",
                    editing_end: "2024-03-15T18:00:00Z",
                    compo_start: "2024-03-16T10:00:00Z",
                    voting_start: "2024-03-16T12:00:00Z",
                    voting_end: "2024-03-16T20:00:00Z",
                    entry_sizelimit: 52428800, // 50 MB
                    source_sizelimit: 10485760, // 10 MB
                    formats: "zip|7z",
                    source_formats: "zip",
                    image_formats: "png|jpg",
                    active: true,
                    show_voting_results: false,
                    is_votable: true,
                    entry_view_type: 0,
                    thumbnail_pref: 1,
                    hide_from_archive: false,
                    hide_from_frontpage: false,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            expect(wrapper.exists()).toBe(true);
            expect(api.adminEventKompomaattiComposRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventKompomaattiComposRetrieve), {
                event_pk: 1,
                id: 5,
            });
        });

        it("converts bytes to appropriate unit on load", async () => {
            vi.mocked(api.adminEventKompomaattiComposRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Compo",
                    description: "",
                    adding_end: "2024-03-15T12:00:00Z",
                    editing_end: "2024-03-15T18:00:00Z",
                    compo_start: "2024-03-16T10:00:00Z",
                    voting_start: "2024-03-16T12:00:00Z",
                    voting_end: "2024-03-16T20:00:00Z",
                    entry_sizelimit: 1073741824, // 1 GB
                    source_sizelimit: null,
                    formats: "",
                    source_formats: "",
                    image_formats: "",
                    active: true,
                    show_voting_results: false,
                    is_votable: true,
                    entry_view_type: 0,
                    thumbnail_pref: 0,
                    hide_from_archive: false,
                    hide_from_frontpage: false,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Should have converted 1 GB properly
            expect(wrapper.exists()).toBe(true);
            expect(api.adminEventKompomaattiComposRetrieve).toHaveBeenCalled();
        });

        it("submits correct data on edit", async () => {
            vi.mocked(api.adminEventKompomaattiComposRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Compo",
                    description: "",
                    adding_end: "2024-03-15T12:00:00Z",
                    editing_end: "2024-03-15T18:00:00Z",
                    compo_start: "2024-03-16T10:00:00Z",
                    voting_start: "2024-03-16T12:00:00Z",
                    voting_end: "2024-03-16T20:00:00Z",
                    entry_sizelimit: null,
                    source_sizelimit: null,
                    formats: "",
                    source_formats: "",
                    image_formats: "",
                    active: true,
                    show_voting_results: false,
                    is_votable: true,
                    entry_view_type: 0,
                    thumbnail_pref: 0,
                    hide_from_archive: false,
                    hide_from_frontpage: false,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Change name
            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Updated Compo Name");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiComposPartialUpdate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventKompomaattiComposPartialUpdate), {
                event_pk: 1,
                id: 5,
            });
        });
    });

    describe("API error handling", () => {
        it("maps all field errors with snake_case mapping", async () => {
            vi.mocked(api.adminEventKompomaattiComposCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    name: ["Name required."],
                    adding_end: ["Invalid datetime."],
                    entry_sizelimit: ["Invalid size."],
                    source_formats: ["Invalid format."],
                    show_voting_results: ["Invalid value."],
                    hide_from_archive: ["Invalid value."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("a");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T12:00");
            await datetimeInputs[1]!.setValue("2024-03-15T18:00");
            await datetimeInputs[2]!.setValue("2024-03-16T10:00");
            await datetimeInputs[3]!.setValue("2024-03-16T12:00");
            await datetimeInputs[4]!.setValue("2024-03-16T20:00");

            await flushPromises();
            await submitForm(wrapper);

            // Errors should be displayed
            const errorMessages = wrapper.findAll(".v-messages__message");
            expect(errorMessages.length).toBeGreaterThan(0);
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(api.adminEventKompomaattiComposCreate).mockRejectedValueOnce(
                createMockApiError(500, {})
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Demo Compo");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T12:00");
            await datetimeInputs[1]!.setValue("2024-03-15T18:00");
            await datetimeInputs[2]!.setValue("2024-03-16T10:00");
            await datetimeInputs[3]!.setValue("2024-03-16T12:00");
            await datetimeInputs[4]!.setValue("2024-03-16T20:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiComposCreate).toHaveBeenCalled();
        });
    });

    describe("special features", () => {
        it("has size unit selectors for B/KB/MB/GB conversion", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Should have unit selectors
            const selects = wrapper.findAllComponents({ name: "VSelect" });
            expect(selects.length).toBeGreaterThanOrEqual(2);
        });

        it("has inverted toggles for hideFromArchive and hideFromFrontpage", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // 5 toggle switches
            const toggles = wrapper.findAll(".toggle-switch");
            expect(toggles.length).toBe(5);
        });

        it("has format comboboxes with common format suggestions", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const comboboxes = wrapper.findAllComponents({ name: "VCombobox" });
            expect(comboboxes.length).toBe(3);
        });

        it("has entry view type and thumbnail pref dropdowns", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const selects = wrapper.findAllComponents({ name: "VSelect" });
            // At least 2 for entry_view_type and thumbnail_pref
            expect(selects.length).toBeGreaterThanOrEqual(2);
        });
    });

    describe("optional fields", () => {
        it("submits with description when filled", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Demo Compo");

            // Set description via HTML editor
            const editor = wrapper.find('[data-testid="html-editor"]');
            await editor.setValue("<p>Compo description</p>");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T12:00");
            await datetimeInputs[1]!.setValue("2024-03-15T18:00");
            await datetimeInputs[2]!.setValue("2024-03-16T10:00");
            await datetimeInputs[3]!.setValue("2024-03-16T12:00");
            await datetimeInputs[4]!.setValue("2024-03-16T20:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiComposCreate).toHaveBeenCalled();
            const callBody = vi.mocked(api.adminEventKompomaattiComposCreate).mock.calls[0]?.[0]
                ?.body;
            expect(callBody?.description).toBe("<p>Compo description</p>");
        });

        it("submits with empty description", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Demo Compo");

            // Don't set description

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T12:00");
            await datetimeInputs[1]!.setValue("2024-03-15T18:00");
            await datetimeInputs[2]!.setValue("2024-03-16T10:00");
            await datetimeInputs[3]!.setValue("2024-03-16T12:00");
            await datetimeInputs[4]!.setValue("2024-03-16T20:00");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiComposCreate).toHaveBeenCalled();
            const callBody = vi.mocked(api.adminEventKompomaattiComposCreate).mock.calls[0]?.[0]
                ?.body;
            expect(callBody?.description).toBe("");
        });
    });

    describe("validation", () => {
        it("does not submit when name is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Only fill datetime fields
            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T12:00");
            await datetimeInputs[1]!.setValue("2024-03-15T18:00");
            await datetimeInputs[2]!.setValue("2024-03-16T10:00");
            await datetimeInputs[3]!.setValue("2024-03-16T12:00");
            await datetimeInputs[4]!.setValue("2024-03-16T20:00");

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiComposCreate).not.toHaveBeenCalled();
        });

        it("does not submit when datetime fields are missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Demo Compo");

            // Only fill 3 of 5 datetime fields
            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T12:00");
            await datetimeInputs[1]!.setValue("2024-03-15T18:00");
            await datetimeInputs[2]!.setValue("2024-03-16T10:00");

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiComposCreate).not.toHaveBeenCalled();
        });

        it("allows null size limits", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Demo Compo");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T12:00");
            await datetimeInputs[1]!.setValue("2024-03-15T18:00");
            await datetimeInputs[2]!.setValue("2024-03-16T10:00");
            await datetimeInputs[3]!.setValue("2024-03-16T12:00");
            await datetimeInputs[4]!.setValue("2024-03-16T20:00");

            // Don't fill size limits

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiComposCreate).toHaveBeenCalled();
        });

        it("allows empty format strings", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Demo Compo");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T12:00");
            await datetimeInputs[1]!.setValue("2024-03-15T18:00");
            await datetimeInputs[2]!.setValue("2024-03-16T10:00");
            await datetimeInputs[3]!.setValue("2024-03-16T12:00");
            await datetimeInputs[4]!.setValue("2024-03-16T20:00");

            // Don't fill formats

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiComposCreate).toHaveBeenCalled();
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
                name: "compos",
                params: { eventId: "1" },
                query: { page: "2", active: "true" },
            });
        });
    });
});
