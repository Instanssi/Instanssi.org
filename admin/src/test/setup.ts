import { vi } from "vitest";

// Mock API (only auth endpoints used by LoginView.test.ts)
vi.mock("@/api", () => ({
    login: vi.fn(),
    logout: vi.fn(),
    userInfo: vi.fn(),
}));

// Mock vue-router
vi.mock("vue-router", () => ({
    useRouter: () => ({
        push: vi.fn(),
    }),
    useRoute: () => ({
        params: {},
    }),
}));

// Mock vue-toastification
vi.mock("vue-toastification", () => ({
    useToast: () => ({
        success: vi.fn(),
        error: vi.fn(),
        warning: vi.fn(),
        info: vi.fn(),
    }),
}));

// Mock vue-i18n
vi.mock("vue-i18n", () => ({
    useI18n: () => ({
        t: (key: string) => key,
        d: (date: string) => date,
    }),
}));

// Mock events service
vi.mock("@/services/events", () => ({
    useEvents: () => ({
        getLatestEvent: () => ({ id: 1, name: "Test Event" }),
        getEventById: (id: number) => ({ id, name: `Event ${id}` }),
        refreshEvents: vi.fn(),
    }),
}));

// Mock auth service
vi.mock("@/services/auth", () => ({
    useAuth: () => ({
        isLoggedIn: () => true,
        canView: () => true,
        canAdd: () => true,
        canChange: () => true,
        canDelete: () => true,
        login: vi.fn(),
        logout: vi.fn(),
        refreshStatus: vi.fn(),
    }),
    PermissionTarget: {
        EVENT: "event",
        USER: "user",
        BLOG_ENTRY: "blogentry",
    },
}));

// Mock symbols (for inject)
vi.mock("@/symbols", () => ({
    confirmDialogKey: Symbol("confirmDialog"),
}));
