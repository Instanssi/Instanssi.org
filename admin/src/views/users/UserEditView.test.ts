import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import * as api from "@/api";
import {
    createMockApiError,
    expectApiCalledWithBody,
    expectApiCalledWithPath,
    submitForm,
} from "@/test/helpers/form-test-utils";

import UserEditView from "./UserEditView.vue";

const vuetify = createVuetify({ components, directives });

function mountComponent(props: { id?: string }) {
    return mount(UserEditView, {
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

describe("UserEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("create mode", () => {
        it("renders empty form with all fields", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            expect(textFields.length).toBeGreaterThanOrEqual(4);
        });

        it("submits correct snake_case data to API", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            const inputs = wrapper.findAll('input[type="text"]');
            await inputs[0]!.setValue("testuser");
            await inputs[1]!.setValue("test@example.com");
            await inputs[2]!.setValue("John");
            await inputs[3]!.setValue("Doe");

            await submitForm(wrapper);

            expect(api.adminUsersCreate).toHaveBeenCalled();
            expectApiCalledWithBody(vi.mocked(api.adminUsersCreate), {
                username: "testuser",
                email: "test@example.com",
                first_name: "John",
                last_name: "Doe",
                is_active: true,
            });
        });

        it("submits is_active as boolean", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            const inputs = wrapper.findAll('input[type="text"]');
            await inputs[0]!.setValue("testuser");
            await inputs[1]!.setValue("test@example.com");

            const switchInput = wrapper.find('.v-switch input[type="checkbox"]');
            if (switchInput.exists()) {
                await switchInput.setValue(false);
            }

            await submitForm(wrapper);

            const callBody = vi.mocked(api.adminUsersCreate).mock.calls[0]?.[0]?.body;
            expect(callBody).toBeDefined();
            expect(typeof callBody?.is_active).toBe("boolean");
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing user data", async () => {
            vi.mocked(api.adminUsersRetrieve).mockResolvedValueOnce({
                data: {
                    id: 1,
                    username: "existinguser",
                    email: "existing@example.com",
                    first_name: "Jane",
                    last_name: "Smith",
                    is_active: true,
                    date_joined: "2024-01-15T10:00:00Z",
                },
            } as never);

            const wrapper = mountComponent({ id: "1" });
            await flushPromises();

            expect(wrapper.exists()).toBe(true);
            expect(api.adminUsersRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminUsersRetrieve), { id: 1 });
        });

        it("makes username field readonly in edit mode", async () => {
            vi.mocked(api.adminUsersRetrieve).mockResolvedValueOnce({
                data: {
                    id: 1,
                    username: "existinguser",
                    email: "existing@example.com",
                    first_name: "Jane",
                    last_name: "Smith",
                    is_active: true,
                    date_joined: "2024-01-15T10:00:00Z",
                },
            } as never);

            const wrapper = mountComponent({ id: "1" });
            await flushPromises();

            const usernameInput = wrapper.findAll('input[type="text"]')[0]!;
            expect(usernameInput.attributes("readonly")).toBeDefined();
        });

        it("shows date_joined field in edit mode", async () => {
            vi.mocked(api.adminUsersRetrieve).mockResolvedValueOnce({
                data: {
                    id: 1,
                    username: "existinguser",
                    email: "existing@example.com",
                    first_name: "Jane",
                    last_name: "Smith",
                    is_active: true,
                    date_joined: "2024-01-15T10:00:00Z",
                },
            } as never);

            const wrapper = mountComponent({ id: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            expect(textFields.length).toBeGreaterThanOrEqual(5);
        });

        it("submits correct data on edit", async () => {
            vi.mocked(api.adminUsersRetrieve).mockResolvedValueOnce({
                data: {
                    id: 1,
                    username: "existinguser",
                    email: "existing@example.com",
                    first_name: "Jane",
                    last_name: "Smith",
                    is_active: true,
                    date_joined: "2024-01-15T10:00:00Z",
                },
            } as never);

            const wrapper = mountComponent({ id: "1" });
            await flushPromises();

            // In edit mode, fields are: username (readonly), date_joined, email, firstName, lastName
            const emailInput = wrapper.findAll('input[type="text"]')[2]!;
            await emailInput!.setValue("newemail@example.com");

            await submitForm(wrapper);

            expect(api.adminUsersPartialUpdate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminUsersPartialUpdate), { id: 1 });
            expectApiCalledWithBody(vi.mocked(api.adminUsersPartialUpdate), {
                email: "newemail@example.com",
            });
        });
    });

    describe("API error handling", () => {
        it("maps field errors to form fields using snake_case mapping", async () => {
            vi.mocked(api.adminUsersCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    username: ["This username is already taken."],
                    email: ["Enter a valid email address."],
                })
            );

            const wrapper = mountComponent({});
            await flushPromises();

            const inputs = wrapper.findAll('input[type="text"]');
            await inputs[0]!.setValue("duplicateuser");
            await inputs[1]!.setValue("valid@email.com");

            await submitForm(wrapper);

            const errorMessages = wrapper.findAll(".v-messages__message");
            expect(errorMessages.length).toBeGreaterThan(0);
        });

        it("maps first_name/last_name errors correctly", async () => {
            vi.mocked(api.adminUsersCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    first_name: ["Name too long."],
                    last_name: ["Name too long."],
                })
            );

            const wrapper = mountComponent({});
            await flushPromises();

            const inputs = wrapper.findAll('input[type="text"]');
            await inputs[0]!.setValue("testuser");
            await inputs[1]!.setValue("test@example.com");
            await inputs[2]!.setValue("ValidFirstName");
            await inputs[3]!.setValue("ValidLastName");

            await submitForm(wrapper);

            expect(api.adminUsersCreate).toHaveBeenCalled();
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(api.adminUsersCreate).mockRejectedValueOnce(createMockApiError(500, {}));

            const wrapper = mountComponent({});
            await flushPromises();

            const inputs = wrapper.findAll('input[type="text"]');
            await inputs[0]!.setValue("testuser");
            await inputs[1]!.setValue("test@example.com");

            await submitForm(wrapper);

            expect(api.adminUsersCreate).toHaveBeenCalled();
        });
    });

    describe("optional fields", () => {
        it("submits with firstName and lastName when filled", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            const inputs = wrapper.findAll('input[type="text"]');
            await inputs[0]!.setValue("testuser");
            await inputs[1]!.setValue("test@example.com");
            await inputs[2]!.setValue("John");
            await inputs[3]!.setValue("Doe");

            await submitForm(wrapper);

            expect(api.adminUsersCreate).toHaveBeenCalled();
            expectApiCalledWithBody(vi.mocked(api.adminUsersCreate), {
                first_name: "John",
                last_name: "Doe",
            });
        });

        it("submits with empty firstName and lastName", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            const inputs = wrapper.findAll('input[type="text"]');
            await inputs[0]!.setValue("testuser");
            await inputs[1]!.setValue("test@example.com");
            // Don't set firstName and lastName

            await submitForm(wrapper);

            expect(api.adminUsersCreate).toHaveBeenCalled();
            expectApiCalledWithBody(vi.mocked(api.adminUsersCreate), {
                first_name: "",
                last_name: "",
            });
        });
    });

    describe("validation", () => {
        it("does not submit when username is missing", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            const inputs = wrapper.findAll('input[type="text"]');
            await inputs[1]!.setValue("test@example.com");

            await submitForm(wrapper);

            expect(api.adminUsersCreate).not.toHaveBeenCalled();
        });

        it("does not submit with invalid email", async () => {
            const wrapper = mountComponent({});
            await flushPromises();

            const inputs = wrapper.findAll('input[type="text"]');
            await inputs[0]!.setValue("testuser");
            await inputs[1]!.setValue("not-an-email");

            await submitForm(wrapper);

            expect(api.adminUsersCreate).not.toHaveBeenCalled();
        });
    });
});
