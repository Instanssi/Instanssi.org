import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Unmock auth service since we're testing it directly
vi.unmock("@/services/auth");

import * as api from "@instanssi/api";
import { LoginResult, PermissionTarget, useAuth } from "@/services/auth";
import { createMockApiError } from "@/test/helpers/form-test-utils";
import { vuetify } from "@/test/helpers/component-stubs";

import LoginView from "./LoginView.vue";

describe("LoginView - social login buttons", () => {
    async function mountWithProviders() {
        vi.mocked(api.getSocialAuthUrls).mockResolvedValue({
            data: [
                {
                    method: "github",
                    url: "/users/github/login/?next=%2Fmanagement",
                    name: "GitHub",
                },
                {
                    method: "sceneid",
                    url: "/users/sceneid/login/?next=%2Fmanagement",
                    name: "SceneID",
                },
            ],
        } as never);
        const wrapper = mount(LoginView, {
            global: {
                plugins: [vuetify],
                stubs: { FontAwesomeIcon: true, LanguageSelector: true },
            },
        });
        await flushPromises();
        return wrapper;
    }

    it("renders a button per provider", async () => {
        const wrapper = await mountWithProviders();
        const github = wrapper.find('a[href="/users/github/login/?next=%2Fmanagement"]');
        const sceneid = wrapper.find('a[href="/users/sceneid/login/?next=%2Fmanagement"]');
        expect(github.exists()).toBe(true);
        expect(github.text()).toContain("GitHub");
        expect(sceneid.exists()).toBe(true);
        expect(sceneid.text()).toContain("SceneID");
    });

    it("renders the SceneID icon in the button text color", async () => {
        const wrapper = await mountWithProviders();
        const sceneid = wrapper.find('a[href="/users/sceneid/login/?next=%2Fmanagement"]');
        const icon = sceneid.find("svg.sceneid-icon");
        expect(icon.exists()).toBe(true);
        expect(icon.attributes("fill")).toBe("currentColor");
    });
});

describe("LoginView - auth service integration", () => {
    const authService = useAuth();

    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(async () => {
        // Reset auth state
        vi.mocked(api.logout).mockResolvedValue({} as never);
        await authService.logout();
    });

    describe("login with permission check", () => {
        it("should allow login when user has view_event permission", async () => {
            vi.mocked(api.login).mockResolvedValue({ status: 200 } as never);
            vi.mocked(api.userInfoRetrieve).mockResolvedValue({
                data: {
                    id: 1,
                    username: "testuser",
                    first_name: "Test",
                    last_name: "User",
                    email: "test@example.com",
                    user_permissions: ["view_event"],
                    is_superuser: false,
                    date_joined: "2024-01-01",
                    language: "",
                },
            } as never);

            const result = await authService.login("testuser", "password");

            expect(result).toBe(LoginResult.SUCCESS);
            expect(authService.isLoggedIn()).toBe(true);
            expect(authService.canView(PermissionTarget.EVENT)).toBe(true);
        });

        it("should deny permission check when user lacks view_event", async () => {
            vi.mocked(api.login).mockResolvedValue({ status: 200 } as never);
            vi.mocked(api.userInfoRetrieve).mockResolvedValue({
                data: {
                    id: 1,
                    username: "testuser",
                    first_name: "Test",
                    last_name: "User",
                    email: "test@example.com",
                    user_permissions: ["view_user"], // No view_event
                    is_superuser: false,
                    date_joined: "2024-01-01",
                    language: "",
                },
            } as never);

            const result = await authService.login("testuser", "password");

            expect(result).toBe(LoginResult.SUCCESS);
            expect(authService.isLoggedIn()).toBe(true);
            expect(authService.canView(PermissionTarget.EVENT)).toBe(false);
        });

        it("should return false on failed login", async () => {
            vi.mocked(api.login).mockRejectedValue(createMockApiError(401));

            const result = await authService.login("testuser", "wrongpassword");

            expect(result).toBe(LoginResult.AUTH_FAILED);
            expect(authService.isLoggedIn()).toBe(false);
        });

        it("should return EMAIL_NOT_VERIFIED when backend returns 401 with code", async () => {
            const error = createMockApiError(401, { code: "email_not_verified" });
            vi.mocked(api.login).mockRejectedValue(error);

            const result = await authService.login("testuser", "password");

            expect(result).toBe(LoginResult.EMAIL_NOT_VERIFIED);
            expect(authService.isLoggedIn()).toBe(false);
        });

        it("should allow superuser to bypass permission checks", async () => {
            vi.mocked(api.login).mockResolvedValue({ status: 200 } as never);
            vi.mocked(api.userInfoRetrieve).mockResolvedValue({
                data: {
                    id: 1,
                    username: "admin",
                    first_name: "Admin",
                    last_name: "User",
                    email: "admin@example.com",
                    user_permissions: [], // No explicit permissions
                    is_superuser: true,
                    date_joined: "2024-01-01",
                    language: "",
                },
            } as never);

            await authService.login("admin", "password");

            expect(authService.canView(PermissionTarget.EVENT)).toBe(true);
            expect(authService.canView(PermissionTarget.USER)).toBe(true);
            expect(authService.canAdd(PermissionTarget.EVENT)).toBe(true);
        });

        it("should clear state on logout", async () => {
            // First login
            vi.mocked(api.login).mockResolvedValue({ status: 200 } as never);
            vi.mocked(api.userInfoRetrieve).mockResolvedValue({
                data: {
                    id: 1,
                    username: "testuser",
                    first_name: "Test",
                    last_name: "User",
                    email: "test@example.com",
                    user_permissions: ["view_event"],
                    is_superuser: false,
                    date_joined: "2024-01-01",
                    language: "",
                },
            } as never);
            await authService.login("testuser", "password");
            expect(authService.isLoggedIn()).toBe(true);

            // Logout
            vi.mocked(api.logout).mockResolvedValue({} as never);
            await authService.logout();

            expect(authService.isLoggedIn()).toBe(false);
            expect(authService.canView(PermissionTarget.EVENT)).toBe(false);
        });
    });
});
