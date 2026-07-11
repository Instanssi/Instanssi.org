import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useRouter } from "vue-router";

import { VMenuStub, vuetify } from "@/test/helpers/component-stubs";

import UserMenu from "./UserMenu.vue";

// Local router mock so router.push can be spied on (global setup mock
// returns a fresh object per call, which cannot be asserted against).
vi.mock("vue-router", () => ({
    useRouter: vi.fn(() => ({ push: vi.fn() })),
}));

// Local auth mock with a mutable user so the email/username fallback
// can be tested (the global setup mock always returns the same user).
const mockUser = {
    id: 1,
    username: "testuser",
    firstName: "Test",
    lastName: "User",
    email: "test@example.com",
    permissions: new Set<string>(),
    isSuperUser: false,
    language: "en",
};
vi.mock("@/services/auth", async () => {
    const { ref } = await import("vue");
    return {
        useAuth: () => ({ userInfo: ref(mockUser) }),
    };
});

function mountComponent() {
    return mount(UserMenu, {
        global: {
            plugins: [vuetify],
            stubs: {
                FontAwesomeIcon: true,
                VMenu: VMenuStub,
            },
        },
    });
}

async function clickItem(wrapper: ReturnType<typeof mountComponent>, text: string) {
    const item = wrapper.findAll(".v-list-item").find((i) => i.text().includes(text));
    expect(item, `menu item containing "${text}"`).toBeDefined();
    await item!.trigger("click");
}

describe("UserMenu", () => {
    beforeEach(() => {
        mockUser.email = "test@example.com";
        mockUser.username = "testuser";
    });

    it("shows the user's email in the activator button", () => {
        const wrapper = mountComponent();
        expect(wrapper.find(".v-btn").text()).toContain("test@example.com");
    });

    it("falls back to username when email is empty", () => {
        mockUser.email = "";
        const wrapper = mountComponent();
        expect(wrapper.find(".v-btn").text()).toContain("testuser");
    });

    it("links to the Django account pages", () => {
        const wrapper = mountComponent();
        for (const href of [
            "/users/profile/",
            "/users/email/",
            "/users/password/change/",
            "/users/3rdparty/",
        ]) {
            expect(wrapper.find(`a[href="${href}"]`).exists(), href).toBe(true);
        }
    });

    it("navigates to the notifications route", async () => {
        const push = vi.fn();
        vi.mocked(useRouter).mockReturnValue({ push } as never);
        const wrapper = mountComponent();
        await clickItem(wrapper, "UserMenu.notifications");
        expect(push).toHaveBeenCalledWith({ name: "notifications" });
    });

    it("navigates to the logout route", async () => {
        const push = vi.fn();
        vi.mocked(useRouter).mockReturnValue({ push } as never);
        const wrapper = mountComponent();
        await clickItem(wrapper, "UserMenu.logout");
        expect(push).toHaveBeenCalledWith({ name: "logout" });
    });
});
