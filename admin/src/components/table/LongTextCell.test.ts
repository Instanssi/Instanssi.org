import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import { VDialogStub, vuetify } from "@/test/helpers/component-stubs";

import LongTextCell from "./LongTextCell.vue";

function mountComponent(props: { value: string | null | undefined; title?: string }) {
    return mount(LongTextCell, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                FontAwesomeIcon: true,
                VDialog: VDialogStub,
            },
        },
    });
}

describe("LongTextCell", () => {
    describe("basic rendering", () => {
        it("renders nothing when value is null", () => {
            const wrapper = mountComponent({ value: null });
            expect(wrapper.find(".long-text-cell").exists()).toBe(false);
        });

        it("renders nothing when value is undefined", () => {
            const wrapper = mountComponent({ value: undefined });
            expect(wrapper.find(".long-text-cell").exists()).toBe(false);
        });

        it("renders icon button when value is provided", () => {
            const wrapper = mountComponent({ value: "Some text" });
            expect(wrapper.find(".long-text-cell").exists()).toBe(true);
            const btn = wrapper.findComponent({ name: "VBtn" });
            expect(btn.exists()).toBe(true);
        });

        it("button has title attribute for accessibility", () => {
            const wrapper = mountComponent({ value: "Some text" });
            const btn = wrapper.findComponent({ name: "VBtn" });
            expect(btn.attributes("title")).toBe("LongTextCell.clickToView");
        });
    });

    describe("dialog behavior", () => {
        it("opens dialog on button click", async () => {
            const wrapper = mountComponent({ value: "Hello world" });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.attributes("data-model-value")).toBe("true");
        });

        it("dialog receives default title from i18n key", async () => {
            const wrapper = mountComponent({ value: "Hello world" });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.text()).toContain("LongTextCell.dialogTitle");
        });

        it("dialog receives custom title when title prop provided", async () => {
            const wrapper = mountComponent({ value: "Hello world", title: "Custom Title" });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.text()).toContain("Custom Title");
        });

        it("dialog content shows the text value with white-space pre-wrap", async () => {
            const wrapper = mountComponent({ value: "Line 1\nLine 2" });
            const btn = wrapper.findComponent({ name: "VBtn" });
            await btn.trigger("click");
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.text()).toContain("Line 1");
            expect(dialog.text()).toContain("Line 2");
            const preWrapDiv = dialog.find("[style*='white-space: pre-wrap']");
            expect(preWrapDiv.exists()).toBe(true);
        });
    });
});
