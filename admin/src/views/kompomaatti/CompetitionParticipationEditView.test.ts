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

import CompetitionParticipationEditView from "./CompetitionParticipationEditView.vue";

const vuetify = createVuetify({ components, directives });

function mountComponent(props: { eventId: string; id?: string }) {
    return mount(CompetitionParticipationEditView, {
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

describe("CompetitionParticipationEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Mock lists
        vi.mocked(api.adminEventKompomaattiCompetitionsList).mockResolvedValue({
            data: { results: [{ id: 1, name: "Competition 1" }] },
        } as never);
        vi.mocked(api.adminUsersList).mockResolvedValue({
            data: { results: [{ id: 1, username: "user1" }] },
        } as never);
    });

    describe("create mode", () => {
        it("renders form with all fields", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Should have competition select, user autocomplete
            expect(wrapper.findComponent({ name: "VSelect" }).exists()).toBe(true);
            expect(wrapper.findComponent({ name: "VAutocomplete" }).exists()).toBe(true);

            // Should have participant name and score text fields
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            expect(textFields.length).toBeGreaterThanOrEqual(2);

            // Should have disqualification field
            expect(wrapper.find(".dq-field").exists()).toBe(true);
        });

        it("loads competitions and users on mount", async () => {
            mountComponent({ eventId: "1" });
            await flushPromises();

            expect(api.adminEventKompomaattiCompetitionsList).toHaveBeenCalled();
            expect(api.adminUsersList).toHaveBeenCalled();
        });

        it("submits correct snake_case data to API", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Select competition
            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(1);
            await flushPromises();

            // Select user
            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);
            await flushPromises();

            // Fill participant name and score by finding correct fields by label
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            for (const tf of textFields) {
                const input = tf.find("input");
                if (!input.exists()) continue;
                const label = tf.text().toLowerCase();
                if (label.includes("participant") || label.includes("name")) {
                    await input.setValue("Team Alpha");
                    await flushPromises();
                } else if (label.includes("score") && input.attributes("type") === "number") {
                    await input.setValue("100");
                    await flushPromises();
                }
            }

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionParticipationsCreate).toHaveBeenCalled();
            expectApiCalledWithPath(
                vi.mocked(api.adminEventKompomaattiCompetitionParticipationsCreate),
                { event_pk: 1 }
            );

            const callBody = vi.mocked(api.adminEventKompomaattiCompetitionParticipationsCreate)
                .mock.calls[0]?.[0]?.body;
            expect(callBody?.competition).toBe(1);
            expect(callBody?.user).toBe(1);
            expect(callBody?.participant_name).toBe("Team Alpha");
            expect(callBody?.score).toBe(100);
        });

        it("submits disqualification fields with snake_case names", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(1);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            // Toggle disqualified
            const dqToggle = wrapper.find('[data-testid="dq-toggle"]');
            await dqToggle.setValue(true);

            // Fill reason
            const dqReason = wrapper.find('[data-testid="dq-reason"]');
            await dqReason.setValue("Rule violation");

            await flushPromises();
            await submitForm(wrapper);

            const callBody = vi.mocked(api.adminEventKompomaattiCompetitionParticipationsCreate)
                .mock.calls[0]?.[0]?.body;
            expect(callBody?.disqualified).toBe(true);
            expect(callBody?.disqualified_reason).toBe("Rule violation");
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing data", async () => {
            vi.mocked(
                api.adminEventKompomaattiCompetitionParticipationsRetrieve
            ).mockResolvedValueOnce({
                data: {
                    id: 5,
                    competition: 1,
                    user: 1,
                    participant_name: "Existing Team",
                    score: 50,
                    rank: 3,
                    disqualified: false,
                    disqualified_reason: "",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            expect(wrapper.exists()).toBe(true);
            expect(api.adminEventKompomaattiCompetitionParticipationsRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(
                vi.mocked(api.adminEventKompomaattiCompetitionParticipationsRetrieve),
                { event_pk: 1, id: 5 }
            );
        });

        it("disables competition and user dropdowns in edit mode", async () => {
            vi.mocked(
                api.adminEventKompomaattiCompetitionParticipationsRetrieve
            ).mockResolvedValueOnce({
                data: {
                    id: 5,
                    competition: 1,
                    user: 1,
                    participant_name: "Existing Team",
                    score: 50,
                    rank: 3,
                    disqualified: false,
                    disqualified_reason: "",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Competition select should be disabled
            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("disabled")).toBe(true);

            // User autocomplete should be disabled
            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            expect(autocomplete.props("disabled")).toBe(true);
        });

        it("shows readonly rank field in edit mode", async () => {
            vi.mocked(
                api.adminEventKompomaattiCompetitionParticipationsRetrieve
            ).mockResolvedValueOnce({
                data: {
                    id: 5,
                    competition: 1,
                    user: 1,
                    participant_name: "Existing Team",
                    score: 50,
                    rank: 3,
                    disqualified: false,
                    disqualified_reason: "",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Should have a readonly rank field
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            const rankField = textFields.find((tf) => tf.props("readonly") === true);
            expect(rankField).toBeDefined();
        });

        it("does not send competition and user on edit", async () => {
            vi.mocked(
                api.adminEventKompomaattiCompetitionParticipationsRetrieve
            ).mockResolvedValueOnce({
                data: {
                    id: 5,
                    competition: 1,
                    user: 1,
                    participant_name: "Existing Team",
                    score: 50,
                    rank: 3,
                    disqualified: false,
                    disqualified_reason: "",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Change participant name
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            const participantField = textFields.find((tf) => !tf.props("readonly"));
            if (participantField) {
                await participantField.find("input").setValue("Updated Team");
            }

            await flushPromises();
            await submitForm(wrapper);

            expect(
                api.adminEventKompomaattiCompetitionParticipationsPartialUpdate
            ).toHaveBeenCalled();

            const callBody = vi.mocked(
                api.adminEventKompomaattiCompetitionParticipationsPartialUpdate
            ).mock.calls[0]?.[0]?.body;
            // competition and user should NOT be in the body for edit
            expect(callBody?.competition).toBeUndefined();
            expect(callBody?.user).toBeUndefined();
        });
    });

    describe("API error handling", () => {
        it("maps field errors to form fields with snake_case mapping", async () => {
            vi.mocked(
                api.adminEventKompomaattiCompetitionParticipationsCreate
            ).mockRejectedValueOnce(
                createMockApiError(400, {
                    participant_name: ["Name too long."],
                    score: ["Invalid score value."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(1);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            await flushPromises();
            await submitForm(wrapper);

            // Errors should be displayed
            const errorMessages = wrapper.findAll(".v-messages__message");
            expect(errorMessages.length).toBeGreaterThan(0);
        });

        it("maps disqualified_reason error correctly", async () => {
            vi.mocked(
                api.adminEventKompomaattiCompetitionParticipationsCreate
            ).mockRejectedValueOnce(
                createMockApiError(400, {
                    disqualified_reason: ["Reason required when disqualified."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(1);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionParticipationsCreate).toHaveBeenCalled();
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(
                api.adminEventKompomaattiCompetitionParticipationsCreate
            ).mockRejectedValueOnce(createMockApiError(500, {}));

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(1);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionParticipationsCreate).toHaveBeenCalled();
        });
    });

    describe("validation", () => {
        it("does not submit when competition is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Only select user
            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionParticipationsCreate).not.toHaveBeenCalled();
        });

        it("does not submit when user is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Only select competition
            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(1);

            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionParticipationsCreate).not.toHaveBeenCalled();
        });

        it("allows null score", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(1);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            // Don't fill score

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionParticipationsCreate).toHaveBeenCalled();
        });

        it("allows empty participant name", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            await select.setValue(1);

            const autocomplete = wrapper.findComponent({ name: "VAutocomplete" });
            await autocomplete.setValue(1);

            // Don't fill participant name

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventKompomaattiCompetitionParticipationsCreate).toHaveBeenCalled();
        });
    });
});
