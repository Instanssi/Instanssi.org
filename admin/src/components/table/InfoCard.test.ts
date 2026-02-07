import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { h } from "vue";

import { vuetify } from "@/test/helpers/component-stubs";

import InfoCard from "./InfoCard.vue";
import InfoRow from "./InfoRow.vue";

function mountComponent(
    props: { title: string },
    slots?: Record<string, () => ReturnType<typeof h>>
) {
    return mount(InfoCard, {
        props,
        slots,
        global: {
            plugins: [vuetify],
        },
    });
}

describe("InfoCard", () => {
    it("renders the title", () => {
        const wrapper = mountComponent({ title: "Customer Info" });
        const title = wrapper.findComponent({ name: "VCardTitle" });
        expect(title.text()).toBe("Customer Info");
    });

    it("renders a v-card with v-table inside", () => {
        const wrapper = mountComponent({ title: "Details" });
        expect(wrapper.findComponent({ name: "VCard" }).exists()).toBe(true);
        expect(wrapper.findComponent({ name: "VTable" }).exists()).toBe(true);
    });

    it("renders slot content inside tbody", () => {
        const wrapper = mountComponent(
            { title: "Info" },
            {
                default: () => h(InfoRow, { label: "Name", value: "John" }),
            }
        );
        const tbody = wrapper.find("tbody");
        expect(tbody.exists()).toBe(true);
        expect(tbody.text()).toContain("Name");
        expect(tbody.text()).toContain("John");
    });
});
