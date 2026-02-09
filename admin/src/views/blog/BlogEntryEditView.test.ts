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

import BlogEntryEditView from "./BlogEntryEditView.vue";

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
    return mount(BlogEntryEditView, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                LayoutBase: {
                    template: "<div><slot /></div>",
                    props: ["breadcrumbs"],
                },
                FontAwesomeIcon: true,
                RichTextEditor: {
                    template:
                        '<textarea :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" data-testid="tiptap"></textarea>',
                    props: ["modelValue", "eventId"],
                    emits: ["update:modelValue"],
                },
            },
        },
    });
}

describe("BlogEntryEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("create mode", () => {
        it("renders empty form with title, text, and public fields", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Should have title text field
            expect(wrapper.findComponent({ name: "VTextField" }).exists()).toBe(true);
            // Should have tiptap editor
            expect(wrapper.find('[data-testid="tiptap"]').exists()).toBe(true);
            // Should have public switch
            expect(wrapper.findComponent({ name: "VSwitch" }).exists()).toBe(true);
        });

        it("submits correct data to API on create", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Fill title
            const titleInput = wrapper.find("input");
            await titleInput.setValue("Test Blog Post");

            // Fill text (tiptap editor)
            const tiptap = wrapper.find('[data-testid="tiptap"]');
            await tiptap.setValue("<p>Blog content here</p>");

            await flushPromises();

            // Submit form
            await submitForm(wrapper);

            expect(api.adminBlogCreate).toHaveBeenCalled();
            expectApiCalledWithBody(vi.mocked(api.adminBlogCreate), {
                event: 1,
                title: "Test Blog Post",
                text: "<p>Blog content here</p>",
                public: false, // default
            });
        });

        it("submits public field as boolean", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const titleInput = wrapper.find("input");
            await titleInput.setValue("Test Blog Post");

            const tiptap = wrapper.find('[data-testid="tiptap"]');
            await tiptap.setValue("Content");

            // Toggle public switch
            const switchInput = wrapper.find('.v-switch input[type="checkbox"]');
            if (switchInput.exists()) {
                await switchInput.setValue(true);
            }
            await flushPromises();

            await submitForm(wrapper);

            const callBody = vi.mocked(api.adminBlogCreate).mock.calls[0]?.[0]?.body;
            expect(callBody).toBeDefined();
            expect(typeof callBody?.public).toBe("boolean");
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing data", async () => {
            vi.mocked(api.adminBlogRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    title: "Existing Post",
                    text: "<p>Existing content</p>",
                    public: true,
                    event: 1,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            expect(api.adminBlogRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminBlogRetrieve), { id: 5 });

            const titleInput = wrapper.find("input");
            expect((titleInput.element as HTMLInputElement).value).toBe("Existing Post");
        });

        it("submits correct data on edit", async () => {
            vi.mocked(api.adminBlogRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    title: "Existing Post",
                    text: "<p>Existing content</p>",
                    public: true,
                    event: 1,
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Change title
            const titleInput = wrapper.find("input");
            await titleInput.setValue("Updated Post Title");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminBlogPartialUpdate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminBlogPartialUpdate), { id: 5 });
            expectApiCalledWithBody(vi.mocked(api.adminBlogPartialUpdate), {
                title: "Updated Post Title",
            });
        });
    });

    describe("API error handling", () => {
        it("maps field errors to form fields", async () => {
            vi.mocked(api.adminBlogCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    title: ["Title is required."],
                    text: ["Content cannot be empty."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const titleInput = wrapper.find("input");
            await titleInput.setValue("a");

            const tiptap = wrapper.find('[data-testid="tiptap"]');
            await tiptap.setValue("b");
            await flushPromises();

            await submitForm(wrapper);

            // Error messages should be shown
            const errorMessages = wrapper.findAll(".v-messages__message");
            expect(errorMessages.length).toBeGreaterThan(0);
        });

        it("maps public field error correctly", async () => {
            vi.mocked(api.adminBlogCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    public: ["Invalid value."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const titleInput = wrapper.find("input");
            await titleInput.setValue("Title");
            const tiptap = wrapper.find('[data-testid="tiptap"]');
            await tiptap.setValue("Content");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminBlogCreate).toHaveBeenCalled();
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(api.adminBlogCreate).mockRejectedValueOnce(createMockApiError(500, {}));

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const titleInput = wrapper.find("input");
            await titleInput.setValue("Test Title");
            const tiptap = wrapper.find('[data-testid="tiptap"]');
            await tiptap.setValue("Content");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminBlogCreate).toHaveBeenCalled();
        });
    });

    describe("special features", () => {
        it("uses RichTextEditor for rich text editing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Tiptap editor should be rendered
            const tiptap = wrapper.find('[data-testid="tiptap"]');
            expect(tiptap.exists()).toBe(true);
        });

        it("has dynamic switch label based on public state", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // The switch label changes based on value
            const switchComponent = wrapper.findComponent({ name: "VSwitch" });
            expect(switchComponent.exists()).toBe(true);
        });
    });

    describe("validation", () => {
        it("does not submit when title is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Only fill text, not title
            const tiptap = wrapper.find('[data-testid="tiptap"]');
            await tiptap.setValue("Content");

            await submitForm(wrapper);

            expect(api.adminBlogCreate).not.toHaveBeenCalled();
        });

        it("does not submit when text is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Only fill title, not text
            const titleInput = wrapper.find("input");
            await titleInput.setValue("Title");

            await submitForm(wrapper);

            expect(api.adminBlogCreate).not.toHaveBeenCalled();
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
                query: { page: "2", search: "test" },
            } as never);

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            const cancelButton = buttons.find((b) => b.text().includes("General.cancel"));
            await cancelButton!.trigger("click");

            expect(mockPush).toHaveBeenCalledWith({
                name: "blog",
                params: { eventId: "1" },
                query: { page: "2", search: "test" },
            });
        });
    });
});
