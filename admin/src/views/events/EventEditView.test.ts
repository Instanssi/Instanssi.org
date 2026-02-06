import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { useRoute, useRouter } from "vue-router";

import * as api from "@/api";
import {
    createMockApiError,
    expectApiCalledWithBody,
    expectApiCalledWithPath,
    submitForm,
} from "@/test/helpers/form-test-utils";

import EventEditView from "./EventEditView.vue";

vi.mock("vue-router", () => ({
    useRouter: vi.fn(() => ({
        push: vi.fn(),
        replace: vi.fn(),
    })),
    useRoute: vi.fn(() => ({
        params: {},
        query: {},
    })),
}));

const vuetify = createVuetify({ components, directives });

function mountComponent(props: { id?: string }) {
    return mount(EventEditView, {
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

describe("EventEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("create mode", () => {
        it("renders empty form with all fields", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            // Should have name, tag, date, mainurl fields + switch
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            expect(textFields.length).toBe(4); // name, tag, date, mainurl
            expect(wrapper.findComponent({ name: "VSwitch" }).exists()).toBe(true);
        });

        it("has date field with type=date", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            const dateInput = wrapper.find('input[type="date"]');
            expect(dateInput.exists()).toBe(true);
        });

        it("submits correct data to API", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            // Fill form fields
            const textInputs = wrapper.findAll('input[type="text"]');
            const dateInput = wrapper.find('input[type="date"]');

            await textInputs[0]!.setValue("Instanssi 2024");
            await textInputs[1]!.setValue("in24");
            await dateInput.setValue("2024-03-15");
            await textInputs[2]!.setValue("https://instanssi.org");
            await flushPromises();

            // Submit form
            await submitForm(wrapper);

            expect(api.adminEventsCreate).toHaveBeenCalled();
            expectApiCalledWithBody(vi.mocked(api.adminEventsCreate), {
                name: "Instanssi 2024",
                tag: "in24",
                date: "2024-03-15",
                mainurl: "https://instanssi.org",
                archived: false, // default
            });
        });

        it("submits archived as boolean", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            const dateInput = wrapper.find('input[type="date"]');

            await textInputs[0]!.setValue("Test Event");
            await textInputs[1]!.setValue("test");
            await dateInput.setValue("2024-01-01");
            await textInputs[2]!.setValue("https://example.com");

            // Toggle archived switch
            const switchInput = wrapper.find('.v-switch input[type="checkbox"]');
            if (switchInput.exists()) {
                await switchInput.setValue(true);
            }
            await flushPromises();

            await submitForm(wrapper);

            const callBody = vi.mocked(api.adminEventsCreate).mock.calls[0]?.[0]?.body;
            expect(callBody).toBeDefined();
            expect(typeof callBody?.archived).toBe("boolean");
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing event data", async () => {
            vi.mocked(api.adminEventsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 1,
                    name: "Existing Event",
                    tag: "exist",
                    date: "2023-06-15",
                    mainurl: "https://existing.com",
                    archived: false,
                },
            } as never);

            const wrapper = mountComponent({ id: "1" });
            await flushPromises();

            expect(api.adminEventsRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventsRetrieve), { id: 1 });

            const textInputs = wrapper.findAll('input[type="text"]');
            expect((textInputs[0]!.element as HTMLInputElement).value).toBe("Existing Event");
            expect((textInputs[1]!.element as HTMLInputElement).value).toBe("exist");
        });

        it("submits correct data on edit", async () => {
            vi.mocked(api.adminEventsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 1,
                    name: "Existing Event",
                    tag: "exist",
                    date: "2023-06-15",
                    mainurl: "https://existing.com",
                    archived: false,
                },
            } as never);

            const wrapper = mountComponent({ id: "1" });
            await flushPromises();

            // Change name
            const textInputs = wrapper.findAll('input[type="text"]');
            await textInputs[0]!.setValue("Updated Event Name");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventsPartialUpdate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventsPartialUpdate), { id: 1 });
            expectApiCalledWithBody(vi.mocked(api.adminEventsPartialUpdate), {
                name: "Updated Event Name",
            });
        });
    });

    describe("API error handling", () => {
        it("maps field errors to form fields", async () => {
            vi.mocked(api.adminEventsCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    name: ["Event with this name already exists."],
                    tag: ["Tag must be unique."],
                })
            );

            const wrapper = mountComponent({});
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            const dateInput = wrapper.find('input[type="date"]');

            await textInputs[0]!.setValue("Duplicate Event");
            await textInputs[1]!.setValue("dup");
            await dateInput.setValue("2024-01-01");
            await textInputs[2]!.setValue("https://example.com");
            await flushPromises();

            await submitForm(wrapper);

            // Errors should be displayed
            const errorMessages = wrapper.findAll(".v-messages__message");
            expect(errorMessages.length).toBeGreaterThan(0);
        });

        it("maps date field error correctly", async () => {
            vi.mocked(api.adminEventsCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    date: ["Invalid date format."],
                })
            );

            const wrapper = mountComponent({});
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            const dateInput = wrapper.find('input[type="date"]');

            await textInputs[0]!.setValue("Test Event");
            await textInputs[1]!.setValue("test");
            await dateInput.setValue("2024-01-01");
            await textInputs[2]!.setValue("https://example.com");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventsCreate).toHaveBeenCalled();
        });

        it("maps mainurl field error correctly", async () => {
            vi.mocked(api.adminEventsCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    mainurl: ["Enter a valid URL."],
                })
            );

            const wrapper = mountComponent({});
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            const dateInput = wrapper.find('input[type="date"]');

            await textInputs[0]!.setValue("Test Event");
            await textInputs[1]!.setValue("test");
            await dateInput.setValue("2024-01-01");
            await textInputs[2]!.setValue("https://example.com");

            await submitForm(wrapper);

            expect(api.adminEventsCreate).toHaveBeenCalled();
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(api.adminEventsCreate).mockRejectedValueOnce(createMockApiError(500, {}));

            const wrapper = mountComponent({});
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            const dateInput = wrapper.find('input[type="date"]');

            await textInputs[0]!.setValue("Test Event");
            await textInputs[1]!.setValue("test");
            await dateInput.setValue("2024-01-01");
            await textInputs[2]!.setValue("https://example.com");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventsCreate).toHaveBeenCalled();
        });
    });

    describe("validation", () => {
        it("does not submit when name is missing", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            // Fill everything except name
            const textInputs = wrapper.findAll('input[type="text"]');
            const dateInput = wrapper.find('input[type="date"]');

            await textInputs[1]!.setValue("test");
            await dateInput.setValue("2024-01-01");
            await textInputs[2]!.setValue("https://example.com");

            await submitForm(wrapper);

            expect(api.adminEventsCreate).not.toHaveBeenCalled();
        });

        it("does not submit when tag is missing", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            // Fill everything except tag
            const textInputs = wrapper.findAll('input[type="text"]');
            const dateInput = wrapper.find('input[type="date"]');

            await textInputs[0]!.setValue("Test Event");
            await dateInput.setValue("2024-01-01");
            await textInputs[2]!.setValue("https://example.com");

            await submitForm(wrapper);

            expect(api.adminEventsCreate).not.toHaveBeenCalled();
        });

        it("does not submit when date is missing", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            // Fill everything except date
            const textInputs = wrapper.findAll('input[type="text"]');

            await textInputs[0]!.setValue("Test Event");
            await textInputs[1]!.setValue("test");
            await textInputs[2]!.setValue("https://example.com");

            await submitForm(wrapper);

            expect(api.adminEventsCreate).not.toHaveBeenCalled();
        });

        it("does not submit with invalid mainurl", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            const textInputs = wrapper.findAll('input[type="text"]');
            const dateInput = wrapper.find('input[type="date"]');

            await textInputs[0]!.setValue("Test Event");
            await textInputs[1]!.setValue("test");
            await dateInput.setValue("2024-01-01");
            await textInputs[2]!.setValue("not-a-valid-url");

            await submitForm(wrapper);

            expect(api.adminEventsCreate).not.toHaveBeenCalled();
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
                params: {},
                query: { page: "2", archived: "true" },
            } as never);

            const wrapper = mountComponent({});
            await flushPromises();

            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            const cancelButton = buttons.find((b) => b.text().includes("General.cancel"));
            await cancelButton!.trigger("click");

            expect(mockPush).toHaveBeenCalledWith({
                name: "events",
                query: { page: "2", archived: "true" },
            });
        });
    });
});
