import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import { vuetify } from "@/test/helpers/component-stubs";

import InfoRow from "./InfoRow.vue";

function mountComponent(
    props: { label: string; value?: string | number | null },
    slots?: Record<string, () => string>
) {
    return mount(InfoRow, {
        props,
        slots,
        global: {
            plugins: [vuetify],
        },
    });
}

describe("InfoRow", () => {
    it("renders label in bold", () => {
        const wrapper = mountComponent({ label: "Email" });
        const labelCell = wrapper.find("td.font-weight-bold");
        expect(labelCell.exists()).toBe(true);
        expect(labelCell.text()).toBe("Email");
    });

    it("renders string value", () => {
        const wrapper = mountComponent({ label: "Name", value: "John Doe" });
        const cells = wrapper.findAll("td");
        expect(cells).toHaveLength(2);
        expect(cells[1]!.text()).toBe("John Doe");
    });

    it("renders number value", () => {
        const wrapper = mountComponent({ label: "Count", value: 42 });
        const cells = wrapper.findAll("td");
        expect(cells[1]!.text()).toBe("42");
    });

    it("renders empty string for null value", () => {
        const wrapper = mountComponent({ label: "Phone", value: null });
        const cells = wrapper.findAll("td");
        expect(cells[1]!.text()).toBe("");
    });

    it("renders empty string when value is undefined", () => {
        const wrapper = mountComponent({ label: "Phone" });
        const cells = wrapper.findAll("td");
        expect(cells[1]!.text()).toBe("");
    });

    it("renders slot content instead of value prop", () => {
        const wrapper = mountComponent(
            { label: "Status", value: "ignored" },
            {
                default: () => "Custom Content",
            }
        );
        const cells = wrapper.findAll("td");
        expect(cells[1]!.text()).toBe("Custom Content");
    });
});
