import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { nextTick } from "vue";

import { VDialogStub, vuetify } from "@/test/helpers/component-stubs";

import BaseInfoDialog from "./BaseInfoDialog.vue";

interface BaseInfoDialogExposed {
    modal: () => Promise<boolean>;
    setResult: (ok: boolean) => void;
}

function mountComponent(props: {
    title: string;
    width?: number;
    cancelText?: string;
    okText?: string;
    loading?: boolean;
}) {
    return mount(BaseInfoDialog, {
        props,
        slots: {
            default: "<p>Info content</p>",
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

function vm(wrapper: ReturnType<typeof mountComponent>): BaseInfoDialogExposed {
    return wrapper.vm as unknown as BaseInfoDialogExposed;
}

describe("BaseInfoDialog", () => {
    describe("rendering", () => {
        it("renders title when open", async () => {
            const wrapper = mountComponent({ title: "Info Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            expect(wrapper.text()).toContain("Info Title");
            vm(wrapper).setResult(false);
            await promise;
        });

        it("renders slot content in v-card-text when open", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            const cardText = wrapper.findComponent({ name: "VCardText" });
            expect(cardText.text()).toContain("Info content");
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
    });

    describe("buttons", () => {
        it("shows cancel and OK buttons with default i18n text", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            // buttons[0] = X close, buttons[1] = cancel, buttons[2] = OK
            expect(buttons).toHaveLength(3);
            expect(buttons[1]!.text()).toContain("General.cancel");
            expect(buttons[2]!.text()).toContain("General.ok");
            vm(wrapper).setResult(false);
            await promise;
        });

        it("uses custom cancel and OK text", async () => {
            const wrapper = mountComponent({
                title: "Title",
                cancelText: "Nope",
                okText: "Yep",
            });
            const promise = vm(wrapper).modal();
            await nextTick();
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(3);
            expect(buttons[1]!.text()).toContain("Nope");
            expect(buttons[2]!.text()).toContain("Yep");
            vm(wrapper).setResult(false);
            await promise;
        });

        it("cancel button resolves modal to false", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(3);
            await buttons[1]!.trigger("click");
            const result = await promise;
            expect(result).toBe(false);
        });

        it("OK button resolves modal to true", async () => {
            const wrapper = mountComponent({ title: "Title" });
            const promise = vm(wrapper).modal();
            await nextTick();
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(3);
            await buttons[2]!.trigger("click");
            const result = await promise;
            expect(result).toBe(true);
        });
    });
});
