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

import VideoCategoryEditView from "./VideoCategoryEditView.vue";

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
    return mount(VideoCategoryEditView, {
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

describe("VideoCategoryEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("create mode", () => {
        it("renders empty form", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const nameField = wrapper.find("input");
            expect(nameField.exists()).toBe(true);
        });

        it("does not submit when form is invalid", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideoCategoriesCreate).not.toHaveBeenCalled();
        });

        it("submits correct data to API on create", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const input = wrapper.find("input");
            await input.setValue("Test Category");

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideoCategoriesCreate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventArkistoVideoCategoriesCreate), {
                event_pk: 1,
            });
            expectApiCalledWithBody(vi.mocked(api.adminEventArkistoVideoCategoriesCreate), {
                name: "Test Category",
            });
        });

        it("shows success toast after successful create", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const input = wrapper.find("input");
            await input.setValue("Test Category");

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideoCategoriesCreate).toHaveBeenCalled();
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing data", async () => {
            vi.mocked(api.adminEventArkistoVideoCategoriesRetrieve).mockResolvedValueOnce({
                data: { id: 5, name: "Existing Category" },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            expect(api.adminEventArkistoVideoCategoriesRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventArkistoVideoCategoriesRetrieve), {
                event_pk: 1,
                id: 5,
            });

            const input = wrapper.find("input");
            expect((input.element as HTMLInputElement).value).toBe("Existing Category");
        });

        it("submits correct data to API on edit", async () => {
            vi.mocked(api.adminEventArkistoVideoCategoriesRetrieve).mockResolvedValueOnce({
                data: { id: 5, name: "Existing Category" },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            const input = wrapper.find("input");
            await input.setValue("Updated Category");

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideoCategoriesPartialUpdate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventArkistoVideoCategoriesPartialUpdate), {
                event_pk: 1,
                id: 5,
            });
            expectApiCalledWithBody(vi.mocked(api.adminEventArkistoVideoCategoriesPartialUpdate), {
                name: "Updated Category",
            });
        });
    });

    describe("API error handling", () => {
        it("maps field errors to form fields", async () => {
            vi.mocked(api.adminEventArkistoVideoCategoriesCreate).mockRejectedValueOnce(
                createMockApiError(400, { name: ["This name is already taken."] })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const input = wrapper.find("input");
            await input.setValue("Duplicate Name");

            await submitForm(wrapper);

            const errorMessages = wrapper.find(".v-messages__message");
            expect(errorMessages.exists()).toBe(true);
            expect(errorMessages.text()).toContain("This name is already taken.");
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(api.adminEventArkistoVideoCategoriesCreate).mockRejectedValueOnce(
                createMockApiError(500, {})
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const input = wrapper.find("input");
            await input.setValue("Test Category");

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideoCategoriesCreate).toHaveBeenCalled();
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
                query: { page: "2" },
            } as never);

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            const cancelButton = buttons.find((b) => b.text().includes("General.cancel"));
            await cancelButton!.trigger("click");

            expect(mockPush).toHaveBeenCalledWith({
                name: "arkisto-categories",
                params: { eventId: "1" },
                query: { page: "2" },
            });
        });
    });
});
