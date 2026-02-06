import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { nextTick } from "vue";

import { VDialogStub, vuetify } from "@/test/helpers/component-stubs";

import BaseDialog from "./BaseDialog.vue";

interface BaseDialogExposed {
    modal: () => Promise<boolean>;
    setResult: (ok: boolean) => void;
}

function mountComponent(props: { title: string; width?: number }) {
    return mount(BaseDialog, {
        props,
        slots: {
            default: "<p>Dialog content</p>",
        },
        global: {
            plugins: [vuetify],
            stubs: {
                FontAwesomeIcon: true,
                VDialog: VDialogStub,
            },
        },
    });
}

function vm(wrapper: ReturnType<typeof mountComponent>): BaseDialogExposed {
    return wrapper.vm as unknown as BaseDialogExposed;
}

describe("BaseDialog", () => {
    describe("rendering", () => {
        it("renders title from prop when open", async () => {
            const wrapper = mountComponent({ title: "Test Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            expect(wrapper.text()).toContain("Test Title");
            vm(wrapper).setResult(false);
            await promise;
        });

        it("renders slot content when open", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            expect(wrapper.text()).toContain("Dialog content");
            vm(wrapper).setResult(false);
            await promise;
        });

        it("uses default width of 600", () => {
            const wrapper = mountComponent({ title: "Title" });
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.attributes("data-width")).toBe("600");
        });

        it("uses custom width", () => {
            const wrapper = mountComponent({ title: "Title", width: 800 });
            const dialog = wrapper.find(".v-dialog-stub");
            expect(dialog.attributes("data-width")).toBe("800");
        });

        it("dialog is closed initially", () => {
            const wrapper = mountComponent({ title: "Title" });
            expect(wrapper.find(".v-dialog-stub").attributes("data-model-value")).toBe("false");
        });
    });

    describe("modal() flow", () => {
        it("opens dialog when modal() is called", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            expect(wrapper.find(".v-dialog-stub").attributes("data-model-value")).toBe("true");
            vm(wrapper).setResult(false);
            await promise;
        });

        it("emits open event when modal() is called", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            expect(wrapper.emitted("open")).toHaveLength(1);
            vm(wrapper).setResult(false);
            await promise;
        });

        it("resolves to false when setResult(false) is called", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            vm(wrapper).setResult(false);
            const result = await promise;
            expect(result).toBe(false);
        });

        it("resolves to true when setResult(true) is called", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            vm(wrapper).setResult(true);
            const result = await promise;
            expect(result).toBe(true);
        });

        it("closes dialog after resolving", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            vm(wrapper).setResult(true);
            await promise;
            await nextTick();
            expect(wrapper.find(".v-dialog-stub").attributes("data-model-value")).toBe("false");
        });

        it("emits close event after resolving", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            vm(wrapper).setResult(false);
            await promise;
            expect(wrapper.emitted("close")).toHaveLength(1);
        });

        it("close button resolves modal to false", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            const closeBtn = wrapper.findComponent({ name: "VBtn" });
            await closeBtn.trigger("click");
            const result = await promise;
            expect(result).toBe(false);
        });
    });
});
