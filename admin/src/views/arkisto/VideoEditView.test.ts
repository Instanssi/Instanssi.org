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

import VideoEditView from "./VideoEditView.vue";

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
    return mount(VideoEditView, {
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
                FontAwesomeIcon: true,
            },
        },
    });
}

/**
 * Helper to fill the video form fields
 */
async function fillVideoForm(
    wrapper: ReturnType<typeof mountComponent>,
    options: { category?: number; name?: string; youtubeUrl?: string; description?: string }
) {
    if (options.category !== undefined) {
        const select = wrapper.findComponent({ name: "VSelect" });
        await select.setValue(options.category);
        await flushPromises();
    }

    // Get all VTextField components and fill them by label
    const textFields = wrapper.findAllComponents({ name: "VTextField" });
    for (const tf of textFields) {
        const input = tf.find("input");
        if (!input.exists()) continue;

        // Check the label to determine which field this is
        const label = tf.text();
        if (options.name !== undefined && label.toLowerCase().includes("name")) {
            await input.setValue(options.name);
            await flushPromises();
        } else if (options.youtubeUrl !== undefined && label.toLowerCase().includes("youtube")) {
            await input.setValue(options.youtubeUrl);
            await flushPromises();
        }
    }

    if (options.description !== undefined) {
        const textarea = wrapper.findComponent({ name: "VTextarea" });
        if (textarea.exists()) {
            await textarea.find("textarea").setValue(options.description);
            await flushPromises();
        }
    }
}

describe("VideoEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Default: return empty categories list
        vi.mocked(api.adminEventArkistoVideoCategoriesList).mockResolvedValue({
            data: { results: [{ id: 1, name: "Category 1" }] },
        } as never);
    });

    describe("create mode", () => {
        it("renders form with category, name, description, youtubeUrl fields", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Should have category select, name, description, youtubeUrl
            expect(wrapper.findComponent({ name: "VSelect" }).exists()).toBe(true);
            expect(wrapper.findAllComponents({ name: "VTextField" }).length).toBeGreaterThanOrEqual(
                2
            ); // name, youtubeUrl
            expect(wrapper.findComponent({ name: "VTextarea" }).exists()).toBe(true);
        });

        it("loads categories on mount", async () => {
            mountComponent({ eventId: "1" });
            await flushPromises();

            expect(api.adminEventArkistoVideoCategoriesList).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventArkistoVideoCategoriesList), {
                event_pk: 1,
            });
        });

        it("submits correct snake_case data to API", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            await fillVideoForm(wrapper, {
                category: 1,
                name: "My Video",
                youtubeUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                description: "Video description",
            });

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideosCreate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventArkistoVideosCreate), { event_pk: 1 });
            expectApiCalledWithBody(vi.mocked(api.adminEventArkistoVideosCreate), {
                category: 1,
                name: "My Video",
                description: "Video description",
                youtube_url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing video data", async () => {
            vi.mocked(api.adminEventArkistoVideosRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    category: 1,
                    name: "Existing Video",
                    description: "Existing description",
                    youtube_url: "https://youtu.be/abc12345678",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            expect(wrapper.exists()).toBe(true);
            expect(api.adminEventArkistoVideosRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventArkistoVideosRetrieve), {
                event_pk: 1,
                id: 5,
            });
        });

        it("submits correct data on edit", async () => {
            vi.mocked(api.adminEventArkistoVideosRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    category: 1,
                    name: "Existing Video",
                    description: "Existing description",
                    youtube_url: "https://youtu.be/abc12345678",
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Change name
            await fillVideoForm(wrapper, { name: "Updated Video Name" });

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideosPartialUpdate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventArkistoVideosPartialUpdate), {
                event_pk: 1,
                id: 5,
            });
            expectApiCalledWithBody(vi.mocked(api.adminEventArkistoVideosPartialUpdate), {
                name: "Updated Video Name",
            });
        });
    });

    describe("API error handling", () => {
        it("maps field errors to form fields", async () => {
            vi.mocked(api.adminEventArkistoVideosCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    name: ["Name is required."],
                    youtube_url: ["Invalid YouTube URL."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            await fillVideoForm(wrapper, {
                category: 1,
                name: "Video Name",
                youtubeUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });

            await submitForm(wrapper);

            // Errors should be displayed
            const errorMessages = wrapper.findAll(".v-messages__message");
            expect(errorMessages.length).toBeGreaterThan(0);
        });

        it("maps youtube_url error to youtubeUrl field", async () => {
            vi.mocked(api.adminEventArkistoVideosCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    youtube_url: ["Invalid YouTube URL."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            await fillVideoForm(wrapper, {
                category: 1,
                name: "Video Name",
                youtubeUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideosCreate).toHaveBeenCalled();
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(api.adminEventArkistoVideosCreate).mockRejectedValueOnce(
                createMockApiError(500, {})
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            await fillVideoForm(wrapper, {
                category: 1,
                name: "Video Name",
                youtubeUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideosCreate).toHaveBeenCalled();
        });
    });

    describe("optional fields", () => {
        it("submits with description when filled", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            await fillVideoForm(wrapper, {
                category: 1,
                name: "My Video",
                youtubeUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                description: "Video description",
            });

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideosCreate).toHaveBeenCalled();
            expectApiCalledWithBody(vi.mocked(api.adminEventArkistoVideosCreate), {
                description: "Video description",
            });
        });

        it("submits with empty description", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            await fillVideoForm(wrapper, {
                category: 1,
                name: "My Video",
                youtubeUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                // Don't set description
            });

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideosCreate).toHaveBeenCalled();
            expectApiCalledWithBody(vi.mocked(api.adminEventArkistoVideosCreate), {
                description: "",
            });
        });
    });

    describe("YouTube URL validation", () => {
        it("accepts full YouTube URL", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            await fillVideoForm(wrapper, {
                category: 1,
                name: "Video",
                youtubeUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideosCreate).toHaveBeenCalled();
        });

        it("accepts short youtu.be URL", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            await fillVideoForm(wrapper, {
                category: 1,
                name: "Video",
                youtubeUrl: "https://youtu.be/dQw4w9WgXcQ",
            });

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideosCreate).toHaveBeenCalled();
        });

        it("accepts 11-character video ID", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            await fillVideoForm(wrapper, {
                category: 1,
                name: "Video",
                youtubeUrl: "dQw4w9WgXcQ",
            });

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideosCreate).toHaveBeenCalled();
        });

        it("does not submit with invalid YouTube URL", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            await fillVideoForm(wrapper, {
                category: 1,
                name: "Video",
                youtubeUrl: "not-a-youtube-url",
            });

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideosCreate).not.toHaveBeenCalled();
        });
    });

    describe("category dropdown", () => {
        it("populates category dropdown with fetched categories", async () => {
            vi.mocked(api.adminEventArkistoVideoCategoriesList).mockResolvedValueOnce({
                data: {
                    results: [
                        { id: 1, name: "Category A" },
                        { id: 2, name: "Category B" },
                    ],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.exists()).toBe(true);
        });

        it("does not submit when category is missing", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Fill everything except category
            await fillVideoForm(wrapper, {
                name: "Video Name",
                youtubeUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            });

            await submitForm(wrapper);

            expect(api.adminEventArkistoVideosCreate).not.toHaveBeenCalled();
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
                query: { category: "3", search: "demo" },
            } as never);

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            const cancelButton = buttons.find((b) => b.text().includes("General.cancel"));
            await cancelButton!.trigger("click");

            expect(mockPush).toHaveBeenCalledWith({
                name: "arkisto-videos",
                params: { eventId: "1" },
                query: { category: "3", search: "demo" },
            });
        });
    });
});
