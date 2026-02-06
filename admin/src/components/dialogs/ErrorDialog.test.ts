import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { nextTick } from "vue";

import { VDialogStub, vuetify } from "@/test/helpers/component-stubs";

import ErrorDialog from "./ErrorDialog.vue";

interface ErrorDialogExposed {
    open: () => Promise<void>;
}

function mountComponent(props: { title: string }) {
    return mount(ErrorDialog, {
        props,
        slots: {
            default: "<p>Something went wrong</p>",
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

function vm(wrapper: ReturnType<typeof mountComponent>): ErrorDialogExposed {
    return wrapper.vm as unknown as ErrorDialogExposed;
}

describe("ErrorDialog", () => {
    describe("rendering", () => {
        it("renders title with error styling when open", async () => {
            const wrapper = mountComponent({ title: "Error Occurred" });
            const promise = vm(wrapper).open();
            await nextTick();
            expect(wrapper.text()).toContain("Error Occurred");
            const errorDiv = wrapper.find(".text-error");
            expect(errorDiv.exists()).toBe(true);
            // Clean up: click OK
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(2);
            await buttons[1]!.trigger("click");
            await promise;
        });

        it("shows warning icon", async () => {
            const wrapper = mountComponent({ title: "Error" });
            const promise = vm(wrapper).open();
            await nextTick();
            const errorDiv = wrapper.find(".text-error");
            const icon = errorDiv.findComponent({ name: "FontAwesomeIcon" });
            expect(icon.exists()).toBe(true);
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(2);
            await buttons[1]!.trigger("click");
            await promise;
        });

        it("renders slot content when open", async () => {
            const wrapper = mountComponent({ title: "Error" });
            const promise = vm(wrapper).open();
            await nextTick();
            expect(wrapper.text()).toContain("Something went wrong");
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(2);
            await buttons[1]!.trigger("click");
            await promise;
        });
    });

    describe("close behavior", () => {
        it("OK button closes the dialog", async () => {
            const wrapper = mountComponent({ title: "Error" });
            const promise = vm(wrapper).open();
            await nextTick();
            expect(wrapper.find(".v-dialog-stub").attributes("data-model-value")).toBe("true");
            // buttons[0] = X close, buttons[1] = OK
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(2);
            await buttons[1]!.trigger("click");
            await promise;
            await nextTick();
            expect(wrapper.find(".v-dialog-stub").attributes("data-model-value")).toBe("false");
        });

        it("X button closes the dialog", async () => {
            const wrapper = mountComponent({ title: "Error" });
            const promise = vm(wrapper).open();
            await nextTick();
            expect(wrapper.find(".v-dialog-stub").attributes("data-model-value")).toBe("true");
            const buttons = wrapper.findAllComponents({ name: "VBtn" });
            expect(buttons).toHaveLength(2);
            await buttons[0]!.trigger("click");
            await promise;
            await nextTick();
            expect(wrapper.find(".v-dialog-stub").attributes("data-model-value")).toBe("false");
        });
    });
});
