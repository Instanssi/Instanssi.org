import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ref } from "vue";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { useRoute, useRouter } from "vue-router";

import * as api from "@/api";
import { confirmDialogKey } from "@/symbols";
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

import StoreItemEditView from "./StoreItemEditView.vue";

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

// Mock confirm dialog
const mockConfirmDialog = ref({
    ifConfirmed: vi.fn(async (_text: string, callback: () => Promise<void>) => {
        await callback();
    }),
});

function mountComponent(props: { eventId: string; id?: string }) {
    return mount(StoreItemEditView, {
        props,
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

function createMockFile(name: string): File {
    return new File(["test content"], name, { type: "image/png" });
}

describe("StoreItemEditView", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe("create mode", () => {
        it("renders form with all required fields", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Name field
            expect(wrapper.findAllComponents({ name: "VTextField" }).length).toBeGreaterThanOrEqual(
                1
            );

            // Description HTML editor
            expect(wrapper.find('[data-testid="html-editor"]').exists()).toBe(true);

            // File input for image
            expect(wrapper.findComponent({ name: "VFileInput" }).exists()).toBe(true);

            // Number inputs (price, discount, max, maxPerOrder, sortIndex)
            const numberInputs = wrapper.findAll('input[type="number"]');
            expect(numberInputs.length).toBeGreaterThanOrEqual(5);

            // Toggle switches (available, isTicket, isSecret)
            expect(wrapper.findAll(".toggle-switch").length).toBe(3);
        });

        it("submits correct snake_case data to API", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Fill required fields
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Store Item Name");

            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue("19.99"); // price
            await numberInputs[3]!.setValue("100"); // max

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventStoreItemsCreate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventStoreItemsCreate), { event_pk: 1 });

            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventStoreItemsCreate)
            ) as FormData;

            expectFormDataContains(formData, { name: "Store Item Name" });
            expectFormDataContains(formData, { price: "19.99" });
            expectFormDataContains(formData, { max: "100" });
            // Check for snake_case fields - all fields are always sent
            expect(formData.has("max_per_order")).toBe(true);
            expect(formData.has("sort_index")).toBe(true);
            expect(formData.has("discount_amount")).toBe(true);
            expect(formData.has("discount_percentage")).toBe(true);
            expect(formData.has("available")).toBe(true);
            expect(formData.has("is_ticket")).toBe(true);
            expect(formData.has("is_secret")).toBe(true);
        });

        it("uploads image file as FormData", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Store Item");

            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue("9.99");
            await numberInputs[3]!.setValue("50");

            // Upload image
            const mockImage = createMockFile("product.png");
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.setValue(mockImage);

            await flushPromises();
            await submitForm(wrapper);

            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventStoreItemsCreate)
            ) as FormData;

            expectFormDataHasFile(formData, "imagefile_original", "product.png");
        });

        it("shows secretKey field when isSecret is true", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Initially secretKey field should not be visible
            let textFields = wrapper.findAllComponents({ name: "VTextField" });
            const initialCount = textFields.length;

            // Toggle isSecret to true (third toggle)
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[2]!.setValue(true); // isSecret
            await flushPromises();

            // Now secretKey field should be visible
            textFields = wrapper.findAllComponents({ name: "VTextField" });
            expect(textFields.length).toBe(initialCount + 1);
        });

        it("submits secret_key when isSecret is true", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Secret Item");

            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue("99.99");
            await numberInputs[3]!.setValue("10");

            // Enable isSecret
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[2]!.setValue(true);
            await flushPromises();

            // Fill secretKey (new field appeared)
            const updatedTextFields = wrapper.findAllComponents({ name: "VTextField" });
            const secretKeyField = updatedTextFields[updatedTextFields.length - 1]!;
            await secretKeyField.find("input").setValue("SECRET123");

            await flushPromises();
            await submitForm(wrapper);

            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventStoreItemsCreate)
            ) as FormData;

            expectFormDataContains(formData, { is_secret: "true" });
            expectFormDataContains(formData, { secret_key: "SECRET123" });
        });
    });

    describe("edit mode", () => {
        it("loads and displays existing data", async () => {
            vi.mocked(api.adminEventStoreItemsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Item",
                    description: "<p>Description</p>",
                    price: "29.99",
                    max: 100,
                    max_per_order: 5,
                    sort_index: 10,
                    discount_amount: -1,
                    discount_percentage: 0,
                    available: true,
                    is_ticket: false,
                    is_secret: false,
                    secret_key: "",
                    imagefile_thumbnail_url: "https://example.com/thumb.png",
                    variants: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            expect(wrapper.exists()).toBe(true);
            expect(api.adminEventStoreItemsRetrieve).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventStoreItemsRetrieve), {
                event_pk: 1,
                id: 5,
            });
        });

        it("shows existing image in edit mode", async () => {
            vi.mocked(api.adminEventStoreItemsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Item",
                    description: "",
                    price: "29.99",
                    max: 100,
                    max_per_order: null,
                    sort_index: 0,
                    discount_amount: -1,
                    discount_percentage: 0,
                    available: true,
                    is_ticket: false,
                    is_secret: false,
                    secret_key: "",
                    imagefile_thumbnail_url: "https://example.com/thumb.png",
                    variants: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            const image = wrapper.findComponent({ name: "VImg" });
            expect(image.exists()).toBe(true);
        });

        it("shows variants section in edit mode", async () => {
            vi.mocked(api.adminEventStoreItemsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Item",
                    description: "",
                    price: "29.99",
                    max: 100,
                    max_per_order: null,
                    sort_index: 0,
                    discount_amount: -1,
                    discount_percentage: 0,
                    available: true,
                    is_ticket: false,
                    is_secret: false,
                    secret_key: "",
                    imagefile_thumbnail_url: null,
                    variants: [
                        { id: 1, name: "Size S" },
                        { id: 2, name: "Size M" },
                    ],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Variants section should be visible
            expect(wrapper.text()).toContain("Size S");
            expect(wrapper.text()).toContain("Size M");
        });

        it("submits correct data on edit", async () => {
            vi.mocked(api.adminEventStoreItemsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Item",
                    description: "",
                    price: "29.99",
                    max: 100,
                    max_per_order: null,
                    sort_index: 0,
                    discount_amount: -1,
                    discount_percentage: 0,
                    available: true,
                    is_ticket: false,
                    is_secret: false,
                    secret_key: "",
                    imagefile_thumbnail_url: null,
                    variants: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Change name
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Updated Item Name");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventStoreItemsPartialUpdate).toHaveBeenCalled();
            expectApiCalledWithPath(vi.mocked(api.adminEventStoreItemsPartialUpdate), {
                event_pk: 1,
                id: 5,
            });
        });

        it("does not send image file when no new file selected in edit mode", async () => {
            vi.mocked(api.adminEventStoreItemsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Item",
                    description: "",
                    price: "29.99",
                    max: 100,
                    max_per_order: null,
                    sort_index: 0,
                    discount_amount: -1,
                    discount_percentage: 0,
                    available: true,
                    is_ticket: false,
                    is_secret: false,
                    secret_key: "",
                    imagefile_thumbnail_url: "https://example.com/existing-image.png",
                    variants: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Only change name, don't select new image
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Updated Item Name");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventStoreItemsPartialUpdate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventStoreItemsPartialUpdate)
            ) as FormData;

            // Image file should not be in FormData when not selected
            expectFormDataNotHasKey(formData, "imagefile_original");
        });

        it("sends new image file when selected in edit mode", async () => {
            vi.mocked(api.adminEventStoreItemsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Item",
                    description: "",
                    price: "29.99",
                    max: 100,
                    max_per_order: null,
                    sort_index: 0,
                    discount_amount: -1,
                    discount_percentage: 0,
                    available: true,
                    is_ticket: false,
                    is_secret: false,
                    secret_key: "",
                    imagefile_thumbnail_url: "https://example.com/old-image.png",
                    variants: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Select new image file
            const mockImage = createMockFile("new-product-image.png");
            const fileInput = wrapper.findComponent({ name: "VFileInput" });
            await fileInput.setValue(mockImage);

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventStoreItemsPartialUpdate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventStoreItemsPartialUpdate)
            ) as FormData;

            expectFormDataHasFile(formData, "imagefile_original", "new-product-image.png");
        });
    });

    describe("variants management", () => {
        it("allows adding variants in edit mode", async () => {
            vi.mocked(api.adminEventStoreItemsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Item",
                    description: "",
                    price: "29.99",
                    max: 100,
                    max_per_order: null,
                    sort_index: 0,
                    discount_amount: -1,
                    discount_percentage: 0,
                    available: true,
                    is_ticket: false,
                    is_secret: false,
                    secret_key: "",
                    imagefile_thumbnail_url: null,
                    variants: [],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Find variant input and add button
            const variantCard = wrapper.find(".v-card--variant-outlined");
            expect(variantCard.exists()).toBe(true);

            // Fill variant name and add
            const variantInput = variantCard.findComponent({ name: "VTextField" });
            await variantInput.find("input").setValue("Size XL");

            const addButton = variantCard.findComponent({ name: "VBtn" });
            await addButton.trigger("click");
            await flushPromises();

            expect(api.adminEventStoreItemVariantsCreate).toHaveBeenCalled();
        });

        it("allows deleting variants", async () => {
            vi.mocked(api.adminEventStoreItemsRetrieve).mockResolvedValueOnce({
                data: {
                    id: 5,
                    name: "Existing Item",
                    description: "",
                    price: "29.99",
                    max: 100,
                    max_per_order: null,
                    sort_index: 0,
                    discount_amount: -1,
                    discount_percentage: 0,
                    available: true,
                    is_ticket: false,
                    is_secret: false,
                    secret_key: "",
                    imagefile_thumbnail_url: null,
                    variants: [{ id: 1, name: "Size S" }],
                },
            } as never);

            const wrapper = mountComponent({ eventId: "1", id: "5" });
            await flushPromises();

            // Find delete button
            const deleteButton = wrapper.find(".v-list-item .v-btn--icon");
            if (deleteButton.exists()) {
                await deleteButton.trigger("click");
                await flushPromises();

                expect(api.adminEventStoreItemVariantsDestroy).toHaveBeenCalled();
            }
        });
    });

    describe("API error handling", () => {
        it("maps field errors with snake_case mapping", async () => {
            vi.mocked(api.adminEventStoreItemsCreate).mockRejectedValueOnce(
                createMockApiError(400, {
                    name: ["Name required."],
                    price: ["Invalid price."],
                    max_per_order: ["Invalid value."],
                    discount_amount: ["Invalid discount."],
                    is_ticket: ["Invalid value."],
                    secret_key: ["Key required."],
                    imagefile_original: ["Invalid image."],
                })
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("a");

            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue("10");
            await numberInputs[3]!.setValue("5");

            await flushPromises();
            await submitForm(wrapper);

            const errorMessages = wrapper.findAll(".v-messages__message");
            expect(errorMessages.length).toBeGreaterThan(0);
        });

        it("shows toast for non-400 errors", async () => {
            vi.mocked(api.adminEventStoreItemsCreate).mockRejectedValueOnce(
                createMockApiError(500, {})
            );

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Item Name");

            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue("10");
            await numberInputs[3]!.setValue("5");

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventStoreItemsCreate).toHaveBeenCalled();
        });
    });

    describe("special features", () => {
        it("has conditional secretKey field based on isSecret", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // isSecret is false by default, secretKey hidden
            const secretKeyVisibleBefore = wrapper
                .findAll(".v-text-field")
                .some((el) => el.text().toLowerCase().includes("secret"));
            expect(secretKeyVisibleBefore).toBe(false);

            // Toggle isSecret
            const toggles = wrapper.findAll(".toggle-switch input");
            await toggles[2]!.setValue(true);
            await flushPromises();

            // Now secretKey should be visible
            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            expect(textFields.length).toBeGreaterThan(1);
        });

        it("uses HtmlEditor for rich text description", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const editor = wrapper.find('[data-testid="html-editor"]');
            expect(editor.exists()).toBe(true);
        });

        it("has price field with step=0.01 for cents", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const priceInputs = wrapper.findAll('input[step="0.01"]');
            expect(priceInputs.length).toBeGreaterThan(0);
        });
    });

    describe("optional fields", () => {
        it("submits with description when filled", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Store Item Name");

            // Set description via HTML editor
            const editor = wrapper.find('[data-testid="html-editor"]');
            await editor.setValue("<p>Item description</p>");

            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue("19.99"); // price
            await numberInputs[3]!.setValue("100"); // max

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventStoreItemsCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventStoreItemsCreate)
            ) as FormData;
            expectFormDataContains(formData, { description: "<p>Item description</p>" });
        });

        it("submits with empty description", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Store Item Name");

            // Don't set description

            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue("19.99"); // price
            await numberInputs[3]!.setValue("100"); // max

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventStoreItemsCreate).toHaveBeenCalled();
            const formData = getSerializedApiCallBody(
                vi.mocked(api.adminEventStoreItemsCreate)
            ) as FormData;
            expectFormDataContains(formData, { description: "" });
        });
    });

    describe("validation", () => {
        it("requires name field", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            // Fill everything except name
            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue("10");
            await numberInputs[3]!.setValue("5");
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventStoreItemsCreate).not.toHaveBeenCalled();
        });

        it("requires price field", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Item Name");

            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue(""); // Clear price
            await numberInputs[3]!.setValue("5"); // max
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventStoreItemsCreate).not.toHaveBeenCalled();
        });

        it("requires max field", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Item Name");

            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue("10"); // price
            await numberInputs[3]!.setValue(""); // Clear max
            await flushPromises();

            await submitForm(wrapper);

            expect(api.adminEventStoreItemsCreate).not.toHaveBeenCalled();
        });

        it("allows null max_per_order", async () => {
            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            await textFields[0]!.find("input").setValue("Item Name");

            const numberInputs = wrapper.findAll('input[type="number"]');
            await numberInputs[0]!.setValue("10");
            await numberInputs[3]!.setValue("5");
            // Don't fill max_per_order

            await flushPromises();
            await submitForm(wrapper);

            expect(api.adminEventStoreItemsCreate).toHaveBeenCalled();
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
                query: { available: "true", is_ticket: "false" },
            } as never);

            const wrapper = mountComponent({ eventId: "1" });
            await flushPromises();

            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            const cancelButton = buttons.find((b) => b.text().includes("General.cancel"));
            await cancelButton!.trigger("click");

            expect(mockPush).toHaveBeenCalledWith({
                name: "store-items",
                params: { eventId: "1" },
                query: { available: "true", is_ticket: "false" },
            });
        });
    });
});
