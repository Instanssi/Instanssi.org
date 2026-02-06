import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import { vuetify } from "@/test/helpers/component-stubs";

import FormatComboboxField from "./FormatComboboxField.vue";

function mountComponent(props: {
    modelValue: string;
    label: string;
    suggestions?: string[];
    errorMessage?: string;
}) {
    return mount(FormatComboboxField, {
        props,
        global: {
            plugins: [vuetify],
        },
    });
}

describe("FormatComboboxField", () => {
    describe("splitting pipe-separated string to array", () => {
        it("splits a pipe-separated string into array for combobox", () => {
            const wrapper = mountComponent({ modelValue: "png|jpg|gif", label: "Formats" });
            const combobox = wrapper.findComponent({ name: "VCombobox" });
            expect(combobox.props("modelValue")).toEqual(["png", "jpg", "gif"]);
        });

        it("handles single format", () => {
            const wrapper = mountComponent({ modelValue: "png", label: "Formats" });
            const combobox = wrapper.findComponent({ name: "VCombobox" });
            expect(combobox.props("modelValue")).toEqual(["png"]);
        });

        it("returns empty array for empty string", () => {
            const wrapper = mountComponent({ modelValue: "", label: "Formats" });
            const combobox = wrapper.findComponent({ name: "VCombobox" });
            expect(combobox.props("modelValue")).toEqual([]);
        });

        it("filters out empty segments from double pipes", () => {
            const wrapper = mountComponent({ modelValue: "png||jpg", label: "Formats" });
            const combobox = wrapper.findComponent({ name: "VCombobox" });
            expect(combobox.props("modelValue")).toEqual(["png", "jpg"]);
        });
    });

    describe("joining array back to pipe-separated string", () => {
        it("emits pipe-separated string when array changes", async () => {
            const wrapper = mountComponent({ modelValue: "png", label: "Formats" });
            const combobox = wrapper.findComponent({ name: "VCombobox" });

            await combobox.vm.$emit("update:modelValue", ["png", "jpg", "webp"]);
            await wrapper.vm.$nextTick();

            const emitted = wrapper.emitted("update:modelValue");
            expect(emitted).toBeTruthy();
            expect(emitted![emitted!.length - 1]).toEqual(["png|jpg|webp"]);
        });

        it("emits empty string when all items removed", async () => {
            const wrapper = mountComponent({ modelValue: "png", label: "Formats" });
            const combobox = wrapper.findComponent({ name: "VCombobox" });

            await combobox.vm.$emit("update:modelValue", []);
            await wrapper.vm.$nextTick();

            const emitted = wrapper.emitted("update:modelValue");
            expect(emitted).toBeTruthy();
            expect(emitted![emitted!.length - 1]).toEqual([""]);
        });
    });

    describe("props forwarding", () => {
        it("passes label to combobox", () => {
            const wrapper = mountComponent({ modelValue: "", label: "File formats" });
            const combobox = wrapper.findComponent({ name: "VCombobox" });
            expect(combobox.props("label")).toBe("File formats");
        });

        it("passes suggestions as items", () => {
            const suggestions = ["png", "jpg", "gif", "webp"];
            const wrapper = mountComponent({
                modelValue: "",
                label: "Formats",
                suggestions,
            });
            const combobox = wrapper.findComponent({ name: "VCombobox" });
            expect(combobox.props("items")).toEqual(suggestions);
        });

        it("passes error message to combobox", () => {
            const wrapper = mountComponent({
                modelValue: "",
                label: "Formats",
                errorMessage: "At least one format required",
            });
            const combobox = wrapper.findComponent({ name: "VCombobox" });
            expect(combobox.props("errorMessages")).toBe("At least one format required");
        });

        it("enables multiple and chips", () => {
            const wrapper = mountComponent({ modelValue: "", label: "Formats" });
            const combobox = wrapper.findComponent({ name: "VCombobox" });
            expect(combobox.props("multiple")).toBe(true);
            expect(combobox.props("chips")).toBe(true);
        });
    });
});
