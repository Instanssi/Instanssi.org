import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";
import { nextTick } from "vue";

import { VDialogStub, vuetify } from "@/test/helpers/component-stubs";

import ConfirmDialog from "./ConfirmDialog.vue";

interface ConfirmDialogExposed {
    confirm: (text: string) => Promise<boolean>;
    ifConfirmed: (text: string, callback: () => Promise<void>) => Promise<void>;
}

function mountComponent() {
    return mount(ConfirmDialog, {
        global: {
            plugins: [vuetify],
            stubs: {
                FontAwesomeIcon: true,
                VDialog: VDialogStub,
            },
        },
    });
}

function vm(wrapper: ReturnType<typeof mountComponent>): ConfirmDialogExposed {
    return wrapper.vm as unknown as ConfirmDialogExposed;
}

describe("ConfirmDialog", () => {
    describe("confirm()", () => {
        it("displays body text when confirm() is called", async () => {
            const wrapper = mountComponent();
            const promise = vm(wrapper).confirm("Are you sure?");
            await nextTick();
            expect(wrapper.text()).toContain("Are you sure?");
            // Clean up: click cancel
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(3);
            await buttons[1]!.trigger("click");
            await promise;
        });

        it("resolves to true when OK is clicked", async () => {
            const wrapper = mountComponent();
            const promise = vm(wrapper).confirm("Delete this?");
            await nextTick();
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            // buttons[0] = X close, buttons[1] = cancel, buttons[2] = OK
            expect(buttons).toHaveLength(3);
            await buttons[2]!.trigger("click");
            const result = await promise;
            expect(result).toBe(true);
        });

        it("resolves to false when cancel is clicked", async () => {
            const wrapper = mountComponent();
            const promise = vm(wrapper).confirm("Delete this?");
            await nextTick();
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(3);
            await buttons[1]!.trigger("click");
            const result = await promise;
            expect(result).toBe(false);
        });
    });

    describe("ifConfirmed()", () => {
        it("calls callback when confirmed", async () => {
            const wrapper = mountComponent();
            const callback = vi.fn().mockResolvedValue(undefined);
            const promise = vm(wrapper).ifConfirmed("Sure?", callback);
            await nextTick();
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(3);
            await buttons[2]!.trigger("click");
            await promise;
            expect(callback).toHaveBeenCalledOnce();
        });

        it("does not call callback when cancelled", async () => {
            const wrapper = mountComponent();
            const callback = vi.fn().mockResolvedValue(undefined);
            const promise = vm(wrapper).ifConfirmed("Sure?", callback);
            await nextTick();
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(3);
            await buttons[1]!.trigger("click");
            await promise;
            expect(callback).not.toHaveBeenCalled();
        });
    });
});
