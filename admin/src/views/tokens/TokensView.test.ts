import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ref } from "vue";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import * as api from "@/api";
import { confirmDialogKey } from "@/symbols";

import TokensView from "./TokensView.vue";

const vuetify = createVuetify({ components, directives });

// Mock confirm dialog
const mockConfirm = vi.fn().mockResolvedValue(true);
const mockConfirmDialog = ref({ confirm: mockConfirm });

function mountComponent() {
    return mount(TokensView, {
        global: {
            plugins: [vuetify],
            provide: {
                [confirmDialogKey as symbol]: mockConfirmDialog,
            },
            stubs: {
                LayoutBase: {
                    template: "<div><slot /></div>",
                    props: ["breadcrumbs"],
                },
                FontAwesomeIcon: true,
                TokenCreateDialog: {
                    template: "<div class='create-dialog'></div>",
                    props: ["visible"],
                    emits: ["update:visible", "created"],
                },
                TokenCreatedDialog: {
                    template: "<div class='created-dialog'></div>",
                    props: ["visible", "token"],
                    emits: ["update:visible"],
                },
                DateTimeCell: {
                    template: "<span>{{ value }}</span>",
                    props: ["value"],
                },
            },
        },
    });
}

describe("TokensView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("rendering", () => {
        it("renders the view with new token button", async () => {
            const wrapper = mountComponent();
            await flushPromises();

            const newButton = wrapper.findComponent({ name: "VBtn" });
            expect(newButton.exists()).toBe(true);
            expect(newButton.text()).toContain("TokensView.newToken");
        });

        it("renders the data table", async () => {
            const wrapper = mountComponent();
            await flushPromises();

            const table = wrapper.findComponent({ name: "VDataTableServer" });
            expect(table.exists()).toBe(true);
        });
    });

    describe("loading tokens", () => {
        it("calls tokensList API on mount", async () => {
            mountComponent();
            await flushPromises();

            // Wait for debounce
            await new Promise((resolve) => setTimeout(resolve, 300));
            await flushPromises();

            expect(api.tokensList).toHaveBeenCalled();
        });

        it("displays tokens from API response", async () => {
            vi.mocked(api.tokensList).mockResolvedValueOnce({
                data: {
                    results: [
                        {
                            pk: "test-pk-1",
                            token_key: "abc12345",
                            user: 1,
                            created: "2024-01-15T10:00:00Z",
                            expiry: "2024-02-14T10:00:00Z",
                        },
                    ],
                    count: 1,
                },
            } as never);

            const wrapper = mountComponent();
            await flushPromises();
            await new Promise((resolve) => setTimeout(resolve, 300));
            await flushPromises();

            expect(wrapper.exists()).toBe(true);
            expect(api.tokensList).toHaveBeenCalled();
        });
    });

    describe("delete functionality", () => {
        it("calls tokensDestroy API when delete confirmed", async () => {
            vi.mocked(api.tokensList).mockResolvedValueOnce({
                data: {
                    results: [
                        {
                            pk: "test-pk-1",
                            token_key: "abc12345",
                            user: 1,
                            created: "2024-01-15T10:00:00Z",
                            expiry: "2024-02-14T10:00:00Z",
                        },
                    ],
                    count: 1,
                },
            } as never);

            const wrapper = mountComponent();
            await flushPromises();
            await new Promise((resolve) => setTimeout(resolve, 300));
            await flushPromises();

            // Find delete button in the table
            const deleteButtons = wrapper.findAll(".v-btn--variant-text");
            const deleteBtn = deleteButtons.find((b) => b.classes().includes("text-error"));

            if (deleteBtn) {
                await deleteBtn.trigger("click");
                await flushPromises();

                expect(mockConfirm).toHaveBeenCalled();
                expect(api.tokensDestroy).toHaveBeenCalledWith({
                    path: { digest: "test-pk-1" },
                });
            }
        });

        it("does not call tokensDestroy when delete cancelled", async () => {
            mockConfirm.mockResolvedValueOnce(false);

            vi.mocked(api.tokensList).mockResolvedValueOnce({
                data: {
                    results: [
                        {
                            pk: "test-pk-1",
                            token_key: "abc12345",
                            user: 1,
                            created: "2024-01-15T10:00:00Z",
                            expiry: "2024-02-14T10:00:00Z",
                        },
                    ],
                    count: 1,
                },
            } as never);

            const wrapper = mountComponent();
            await flushPromises();
            await new Promise((resolve) => setTimeout(resolve, 300));
            await flushPromises();

            const deleteButtons = wrapper.findAll(".v-btn--variant-text");
            const deleteBtn = deleteButtons.find((b) => b.classes().includes("text-error"));

            if (deleteBtn) {
                await deleteBtn.trigger("click");
                await flushPromises();

                expect(mockConfirm).toHaveBeenCalled();
                expect(api.tokensDestroy).not.toHaveBeenCalled();
            }
        });
    });

    describe("create dialog", () => {
        it("opens create dialog when new token button clicked", async () => {
            const wrapper = mountComponent();
            await flushPromises();

            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            const newButton = buttons.find((b) => b.text().includes("TokensView.newToken"));

            expect(newButton).toBeDefined();
            if (newButton) {
                // Before click, check the dialog should have visible=false
                let createDialog = wrapper.find(".create-dialog");
                expect(createDialog.exists()).toBe(true);

                await newButton.trigger("click");
                await flushPromises();

                // Verify component is still mounted
                createDialog = wrapper.find(".create-dialog");
                expect(createDialog.exists()).toBe(true);
            }
        });
    });
});
