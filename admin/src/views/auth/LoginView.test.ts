import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Unmock auth service since we're testing it directly
vi.unmock("@/services/auth");

import * as api from "@/api";
import { PermissionTarget, useAuth } from "@/services/auth";

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

            expect(result).toBe(true);
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

            expect(result).toBe(true);
            expect(authService.isLoggedIn()).toBe(true);
            expect(authService.canView(PermissionTarget.EVENT)).toBe(false);
        });

        it("should return false on failed login", async () => {
            vi.mocked(api.login).mockResolvedValue({ status: 401 } as never);

            const result = await authService.login("testuser", "wrongpassword");

            expect(result).toBe(false);
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
