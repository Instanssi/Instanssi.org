import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import { vuetify } from "@/test/helpers/component-stubs";

import FileSizeInputField from "./FileSizeInputField.vue";

function mountComponent(props: {
    modelValue: number | null;
    label: string;
    errorMessage?: string;
}) {
    return mount(FileSizeInputField, {
        props,
        global: {
            plugins: [vuetify],
        },
    });
}

describe("FileSizeInputField", () => {
    describe("unit selection for initial value", () => {
        it("selects MB for null value", () => {
            const wrapper = mountComponent({ modelValue: null, label: "Size" });
            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("modelValue")).toBe("MB");
        });

        it("selects MB for 0 bytes", () => {
            const wrapper = mountComponent({ modelValue: 0, label: "Size" });
            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("modelValue")).toBe("MB");
        });

        it("selects B for small values", () => {
            const wrapper = mountComponent({ modelValue: 512, label: "Size" });
            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("modelValue")).toBe("B");
        });

        it("selects KB for kilobyte-range values", () => {
            const wrapper = mountComponent({ modelValue: 1024 * 50, label: "Size" });
            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("modelValue")).toBe("KB");
        });

        it("selects MB for megabyte-range values", () => {
            const wrapper = mountComponent({ modelValue: 1024 * 1024 * 5, label: "Size" });
            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("modelValue")).toBe("MB");
        });

        it("selects GB for gigabyte-range values", () => {
            const wrapper = mountComponent({ modelValue: 1024 * 1024 * 1024 * 2, label: "Size" });
            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("modelValue")).toBe("GB");
        });
    });

    describe("display value conversion", () => {
        it("displays null for null modelValue", () => {
            const wrapper = mountComponent({ modelValue: null, label: "Size" });
            const textField = wrapper.findComponent({ name: "VTextField" });
            expect(textField.props("modelValue")).toBeNull();
        });

        it("displays correct value in MB", () => {
            const wrapper = mountComponent({ modelValue: 1024 * 1024 * 5, label: "Size" });
            const textField = wrapper.findComponent({ name: "VTextField" });
            expect(textField.props("modelValue")).toBe(5);
        });

        it("displays correct value in KB", () => {
            const wrapper = mountComponent({ modelValue: 1024 * 100, label: "Size" });
            const textField = wrapper.findComponent({ name: "VTextField" });
            expect(textField.props("modelValue")).toBe(100);
        });

        it("displays correct value in GB", () => {
            const wrapper = mountComponent({ modelValue: 1024 * 1024 * 1024 * 3, label: "Size" });
            const textField = wrapper.findComponent({ name: "VTextField" });
            expect(textField.props("modelValue")).toBe(3);
        });
    });

    describe("emitting updates", () => {
        it("emits bytes when display value changes", async () => {
            const wrapper = mountComponent({ modelValue: 1024 * 1024, label: "Size" });
            const textField = wrapper.findComponent({ name: "VTextField" });

            await textField.vm.$emit("update:modelValue", 10);
            await wrapper.vm.$nextTick();

            const emitted = wrapper.emitted("update:modelValue");
            expect(emitted).toBeTruthy();
            // Should emit 10 MB in bytes
            expect(emitted![emitted!.length - 1]).toEqual([10 * 1024 * 1024]);
        });

        it("emits null when display value is set to null", async () => {
            const wrapper = mountComponent({ modelValue: 1024 * 1024, label: "Size" });
            const textField = wrapper.findComponent({ name: "VTextField" });

            await textField.vm.$emit("update:modelValue", null);
            await wrapper.vm.$nextTick();

            const emitted = wrapper.emitted("update:modelValue");
            expect(emitted).toBeTruthy();
            expect(emitted![emitted!.length - 1]).toEqual([null]);
        });
    });

    describe("props forwarding", () => {
        it("passes label to text field", () => {
            const wrapper = mountComponent({ modelValue: null, label: "Max file size" });
            const textField = wrapper.findComponent({ name: "VTextField" });
            expect(textField.props("label")).toBe("Max file size");
        });

        it("passes error message to text field", () => {
            const wrapper = mountComponent({
                modelValue: null,
                label: "Size",
                errorMessage: "Required field",
            });
            const textField = wrapper.findComponent({ name: "VTextField" });
            expect(textField.props("errorMessages")).toBe("Required field");
        });
    });

    describe("unit change preserves byte value", () => {
        it("does not re-emit value when unit changes", async () => {
            const wrapper = mountComponent({ modelValue: 1024 * 1024 * 5, label: "Size" });
            const select = wrapper.findComponent({ name: "VSelect" });

            // Change unit from MB to GB
            await select.vm.$emit("update:modelValue", "GB");
            await wrapper.vm.$nextTick();

            // Should NOT emit any update — the underlying byte value stays the same
            const emitted = wrapper.emitted("update:modelValue");
            expect(emitted).toBeFalsy();
        });
    });

    describe("auto-selecting best unit on external value change", () => {
        it("switches unit when value changes from null to a value", async () => {
            const wrapper = mountComponent({ modelValue: null, label: "Size" });

            // Initially MB (default for null)
            const select = wrapper.findComponent({ name: "VSelect" });
            expect(select.props("modelValue")).toBe("MB");

            // Simulate external change from null to 2 GB
            await wrapper.setProps({ modelValue: 1024 * 1024 * 1024 * 2 });

            expect(select.props("modelValue")).toBe("GB");
        });
    });
});
