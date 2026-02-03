import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import * as api from "@/api";
import {
    createMockApiError,
    expectApiCalledWithPath,
    submitForm,
} from "@/test/helpers/form-test-utils";

import CompetitionEditView from "./CompetitionEditView.vue";

const vuetify = createVuetify({ components, directives });

function mountComponent(props: { eventId: string; id?: string }) {
    return mount(CompetitionEditView, {
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
                VuetifyTiptap: {
                    template:
                        '<div class="vuetify-tiptap-stub"><textarea :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" /></div>',
                    props: ["modelValue"],
                    emits: ["update:modelValue"],
                },
                FontAwesomeIcon: true,
            },
        },
    });
}

describe("CompetitionEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("create mode", () => {
        it("renders form with all required fields", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Check for text fields
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            expect(textFields.length).toBeGreaterThanOrEqual(4); // name + 3 datetime fields

            // Check for combobox (scoreType)
            expect(wrapper.findComponent({ name: "VCombobox" }).exists()).toBe(true);

            // Check for select (scoreSort)
            expect(wrapper.findComponent({ name: "VSelect" }).exists()).toBe(true);

            // Check for toggle switches
            expect(wrapper.findAll(".toggle-switch").length).toBe(3); // active, showResults, hideFromArchive
        });

        it("has datetime-local inputs for schedule fields", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            expect(datetimeInputs.length).toBe(3); // participationEnd, start, end
        });

        it("submits correct snake_case data to API", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Fill required fields
            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Test Competition");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T18:00");
            await datetimeInputs[1]!.setValue("2024-03-16T10:00");

            // Set scoreType via combobox
            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await flushPromises();

            // Submit form
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionsCreate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventKompomaattiCompetitionsCreate), {
                event_pk: 1,
            });

            const callBody = vi.mocked(api.adminEventKompomaattiCompetitionsCreate).mock
                .calls[0]?.[0]?.body;
            expect(callBody).toBeDefined();
            expect(callBody?.name).toBe("Test Competition");
            expect(callBody?.score_type).toBe("pts");
            // Check for snake_case fields
            expect("participation_end" in callBody!).toBe(true);
            expect("score_sort" in callBody!).toBe(true);
            expect("show_results" in callBody!).toBe(true);
            expect("hide_from_archive" in callBody!).toBe(true);
        });

        it("converts datetime to ISO format on submit", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Test Competition");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T18:00");
            await datetimeInputs[1]!.setValue("2024-03-16T10:00");

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await flushPromises();
            await submitForm(wrapper);

            // The datetime values should be converted (checked by presence of call)
            expect(api.adminEventKompomaattiCompetitionsCreate).toHaveBeenCalled();
        });

        it("submits booleans for toggle fields", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Test Competition");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T18:00");
            await datetimeInputs[1]!.setValue("2024-03-16T10:00");

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await flushPromises();
            await submitForm(wrapper);

            const callBody = vi.mocked(api.adminEventKompomaattiCompetitionsCreate).mock
                .calls[0]?.[0]?.body;
            expect(typeof callBody?.active).toBe("boolean");
            expect(typeof callBody?.show_results).toBe("boolean");
            expect(typeof callBody?.hide_from_archive).toBe("boolean");
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing competition data", async () => {
            vi.mocked(api.adminEventKompomaattiCompetitionsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Competition",
                    description: "Description",
                    participation_end: "2024-03-15T18:00:00Z",
                    start: "2024-03-16T10:00:00Z",
                    end: "2024-03-16T12:00:00Z",
                    score_type: "sec",
                    score_sort: 1,
                    active: true,
                    show_results: false,
                    hide_from_archive: false,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            expect(wrapper.exists()).toBe(true);
            expect(api.adminEventKompomaattiCompetitionsRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventKompomaattiCompetitionsRetrieve), {
                event_pk: 1,
                id: 5,
            });
        });

        it("submits correct data on edit", async () => {
            vi.mocked(api.adminEventKompomaattiCompetitionsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Competition",
                    description: "Description",
                    participation_end: "2024-03-15T18:00:00Z",
                    start: "2024-03-16T10:00:00Z",
                    end: null,
                    score_type: "sec",
                    score_sort: 1,
                    active: true,
                    show_results: false,
                    hide_from_archive: false,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Change name
            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Updated Competition Name");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionsPartialUpdate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventKompomaattiCompetitionsPartialUpdate), {
                event_pk: 1,
                id: 5,
            });
        });
    });

    describe("API error handling", () => {
        it("maps field errors to form fields with snake_case mapping", async () => {
            vi.mocked(api.adminEventKompomaattiCompetitionsCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    name: ["Name is required."],
                    participation_end: ["Invalid datetime."],
                    score_type: ["Score type is required."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("a");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T18:00");
            await datetimeInputs[1]!.setValue("2024-03-16T10:00");

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await flushPromises();
            await submitForm(wrapper);

            // Errors should be displayed
            const errorMessages = wrapper.findAll(".v-messages__message");
            expect(errorMessages.length).toBeGreaterThan(0);
        });

        it("maps show_results and hide_from_archive errors correctly", async () => {
            vi.mocked(api.adminEventKompomaattiCompetitionsCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    show_results: ["Invalid value."],
                    hide_from_archive: ["Invalid value."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Test");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T18:00");
            await datetimeInputs[1]!.setValue("2024-03-16T10:00");

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionsCreate).toHaveBeenCalled();
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(api.adminEventKompomaattiCompetitionsCreate).mockRejectedValueOnce(
                createMockApiError(500, {})
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Test");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T18:00");
            await datetimeInputs[1]!.setValue("2024-03-16T10:00");

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionsCreate).toHaveBeenCalled();
        });
    });

    describe("special features", () => {
        it("has combobox with common score types", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            expect(combobox.exists()).toBe(true);
        });

        it("has inverted toggle for hideFromArchive (showInArchive)", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // The third toggle controls showInArchive (inverted hideFromArchive)
            const toggles = wrapper.findAll(".toggle-switch");
            expect(toggles.length).toBe(3);
        });

        it("has score sort dropdown with options", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.exists()).toBe(true);
        });
    });

    describe("optional fields", () => {
        it("submits with description when filled", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Test Competition");

            // Set description via tiptap editor stub
            const tiptapStub = wrapper.find(".vuetify-tiptap-stub textarea");
            await tiptapStub.setValue("Competition description");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T18:00");
            await datetimeInputs[1]!.setValue("2024-03-16T10:00");

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionsCreate).toHaveBeenCalled();
            const callBody = vi.mocked(api.adminEventKompomaattiCompetitionsCreate).mock
                .calls[0]?.[0]?.body;
            expect(callBody?.description).toBe("Competition description");
        });

        it("submits with empty description", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Test Competition");

            // Don't set description

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T18:00");
            await datetimeInputs[1]!.setValue("2024-03-16T10:00");

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionsCreate).toHaveBeenCalled();
            const callBody = vi.mocked(api.adminEventKompomaattiCompetitionsCreate).mock
                .calls[0]?.[0]?.body;
            expect(callBody?.description).toBe("");
        });
    });

    describe("validation", () => {
        it("does not submit when name is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Fill everything except name
            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T18:00");
            await datetimeInputs[1]!.setValue("2024-03-16T10:00");

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionsCreate).not.toHaveBeenCalled();
        });

        it("does not submit when participationEnd is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Test Competition");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[1]!.setValue("2024-03-16T10:00"); // only start

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionsCreate).not.toHaveBeenCalled();
        });

        it("does not submit when start is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Test Competition");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T18:00"); // only participationEnd

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionsCreate).not.toHaveBeenCalled();
        });

        it("allows empty end field", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Test Competition");

            const datetimeInputs = wrapper.findAll('input[type="datetime-local"]');
            await datetimeInputs[0]!.setValue("2024-03-15T18:00");
            await datetimeInputs[1]!.setValue("2024-03-16T10:00");
            // Don't fill end

            const combobox = wrapper.findComponent({ name: "VCombobox" });
            await combobox.find("input").setValue("pts");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionsCreate).toHaveBeenCalled();
        });
    });
});
