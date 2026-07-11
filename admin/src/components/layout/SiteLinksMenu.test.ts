import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import { VMenuStub, vuetify } from "@/test/helpers/component-stubs";

import SiteLinksMenu from "./SiteLinksMenu.vue";

function mountComponent() {
    return mount(SiteLinksMenu, {
        global: {
            plugins: [vuetify],
            stubs: {
                FontAwesomeIcon: true,
                VMenu: VMenuStub,
            },
        },
    });
}

describe("SiteLinksMenu", () => {
    it("links to the public site pages", () => {
        const wrapper = mountComponent();
        for (const href of ["/", "/kompomaatti/", "/arkisto/"]) {
            expect(wrapper.find(`a[href="${href}"]`).exists(), href).toBe(true);
        }
    });

    it("shows the localized link titles", () => {
        const wrapper = mountComponent();
        for (const key of [
            "MainNavigation.links.index",
            "MainNavigation.links.kompomaatti",
            "MainNavigation.links.arkisto",
        ]) {
            expect(wrapper.text()).toContain(key);
        }
    });
});
