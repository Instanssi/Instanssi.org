import { beforeEach, describe, expect, it, vi } from "vitest";

import { urlBase64ToUint8Array, usePush } from "@/services/push";

// Mock the API module
vi.mock("@/api", () => ({
    publicNotificationsVapidKeyRetrieve: vi.fn(),
    notificationsSubscriptionsCreate: vi.fn(),
    notificationsSubscriptionsList: vi.fn(),
    notificationsSubscriptionsDestroy: vi.fn(),
}));

import {
    notificationsSubscriptionsCreate,
    notificationsSubscriptionsDestroy,
    notificationsSubscriptionsList,
    publicNotificationsVapidKeyRetrieve,
} from "@/api";

// Shorthand for mocking API return values (avoids repeating full AxiosResponse shape)

function mockResolved(fn: unknown, data: unknown): void {
    vi.mocked(fn as (...args: unknown[]) => unknown).mockResolvedValue({ data } as never);
}

describe("urlBase64ToUint8Array", () => {
    it("converts a URL-safe base64 string to a Uint8Array", () => {
        // "hello" in base64 is "aGVsbG8="
        // In URL-safe base64 (no padding): "aGVsbG8"
        const result = urlBase64ToUint8Array("aGVsbG8");
        expect(result).toBeInstanceOf(Uint8Array);
        expect(result.length).toBe(5);
        // "hello" = [104, 101, 108, 108, 111]
        expect(Array.from(result)).toEqual([104, 101, 108, 108, 111]);
    });

    it("handles base64 strings with URL-safe characters", () => {
        // Standard base64 uses + and /, URL-safe uses - and _
        const urlSafe = "A-B_";
        const result = urlBase64ToUint8Array(urlSafe);
        expect(result).toBeInstanceOf(Uint8Array);
        expect(result.length).toBeGreaterThan(0);
    });

    it("handles an empty string", () => {
        const result = urlBase64ToUint8Array("");
        expect(result).toBeInstanceOf(Uint8Array);
        expect(result.length).toBe(0);
    });

    it("correctly pads base64 strings", () => {
        // "a" in base64 is "YQ==" (needs 2 padding chars)
        // Without padding: "YQ"
        const result = urlBase64ToUint8Array("YQ");
        expect(Array.from(result)).toEqual([97]); // 'a' = 97
    });
});

// Helper to set up browser push API mocks
function setupBrowserMocks(options?: {
    pushSupported?: boolean;
    permission?: NotificationPermission;
    existingSubscription?: PushSubscription | null;
}) {
    const {
        pushSupported = true,
        permission = "default",
        existingSubscription = null,
    } = options ?? {};

    const mockUnsubscribe = vi.fn().mockResolvedValue(true);
    const mockGetSubscription = vi.fn().mockResolvedValue(existingSubscription);
    const mockSubscribe = vi.fn().mockResolvedValue({
        endpoint: "https://push.example.com/sub/new",
        getKey: (name: string) => {
            if (name === "p256dh") return new Uint8Array([1, 2, 3]).buffer;
            if (name === "auth") return new Uint8Array([4, 5, 6]).buffer;
            return null;
        },
        unsubscribe: mockUnsubscribe,
    });

    const mockRegistration = {
        pushManager: {
            getSubscription: mockGetSubscription,
            subscribe: mockSubscribe,
        },
    };

    if (pushSupported) {
        Object.defineProperty(navigator, "serviceWorker", {
            value: { ready: Promise.resolve(mockRegistration) },
            writable: true,
            configurable: true,
        });
        Object.defineProperty(window, "PushManager", {
            value: class {},
            writable: true,
            configurable: true,
        });
    } else {
        // Remove properties to simulate unsupported
        Object.defineProperty(navigator, "serviceWorker", {
            value: undefined,
            writable: true,
            configurable: true,
        });
        delete (window as unknown as Record<string, unknown>).PushManager;
    }

    Object.defineProperty(window, "Notification", {
        value: { permission },
        writable: true,
        configurable: true,
    });

    return { mockSubscribe, mockGetSubscription, mockUnsubscribe, mockRegistration };
}

describe("usePush", () => {
    beforeEach(() => {
        vi.resetAllMocks();
        vi.spyOn(console, "error").mockImplementation(() => {});
    });

    describe("init", () => {
        it("sets state to unsupported when serviceWorker is not available", async () => {
            setupBrowserMocks({ pushSupported: false });
            const push = usePush();

            await push.init();

            expect(push.pushState.value).toBe("unsupported");
            expect(push.subscribed.value).toBe(false);
        });

        it("reads Notification.permission when push is supported", async () => {
            setupBrowserMocks({ permission: "granted" });
            const push = usePush();

            await push.init();

            expect(push.pushState.value).toBe("granted");
        });

        it("detects existing subscription", async () => {
            const mockSub = { endpoint: "https://push.example.com/existing" } as PushSubscription;
            setupBrowserMocks({ permission: "granted", existingSubscription: mockSub });
            const push = usePush();

            await push.init();

            expect(push.subscribed.value).toBe(true);
            expect(push.pushState.value).toBe("granted");
        });

        it("sets subscribed to false when no existing subscription", async () => {
            setupBrowserMocks({ permission: "default", existingSubscription: null });
            const push = usePush();

            await push.init();

            expect(push.subscribed.value).toBe(false);
        });
    });

    describe("subscribe", () => {
        it("returns false when VAPID key is empty", async () => {
            setupBrowserMocks();
            mockResolved(publicNotificationsVapidKeyRetrieve, { vapid_public_key: "" });
            const push = usePush();

            const result = await push.subscribe();

            expect(result).toBe(false);
            expect(push.subscribed.value).toBe(false);
        });

        it("sets denied state when permission is denied", async () => {
            const { mockSubscribe } = setupBrowserMocks({ permission: "denied" });
            mockSubscribe.mockRejectedValue(new DOMException("User denied"));
            mockResolved(publicNotificationsVapidKeyRetrieve, {
                vapid_public_key: "test-key",
            });

            const push = usePush();
            const result = await push.subscribe();

            expect(result).toBe(false);
            expect(push.pushState.value).toBe("denied");
        });

        it("subscribes successfully and registers with backend", async () => {
            setupBrowserMocks();
            mockResolved(publicNotificationsVapidKeyRetrieve, {
                vapid_public_key: "test-vapid-key",
            });
            mockResolved(notificationsSubscriptionsCreate, { id: 1 });

            const push = usePush();
            const result = await push.subscribe();

            expect(result).toBe(true);
            expect(push.subscribed.value).toBe(true);
            expect(push.pushState.value).toBe("granted");
            expect(notificationsSubscriptionsCreate).toHaveBeenCalledOnce();
        });
    });

    describe("unsubscribe", () => {
        it("returns true when no active subscription exists", async () => {
            setupBrowserMocks({ existingSubscription: null });
            const push = usePush();

            const result = await push.unsubscribe();

            expect(result).toBe(true);
            expect(push.subscribed.value).toBe(false);
        });

        it("deletes server-side subscription before browser unsubscribe", async () => {
            const mockUnsubscribe = vi.fn().mockResolvedValue(true);
            const mockSub = {
                endpoint: "https://push.example.com/sub/123",
                unsubscribe: mockUnsubscribe,
            } as unknown as PushSubscription;
            setupBrowserMocks({ existingSubscription: mockSub });
            mockResolved(notificationsSubscriptionsList, [
                {
                    id: 42,
                    endpoint: "https://push.example.com/sub/123",
                    p256dh: "k",
                    auth: "a",
                    created_at: "",
                },
            ]);

            const callOrder: string[] = [];
            vi.mocked(notificationsSubscriptionsDestroy).mockImplementation((async () => {
                callOrder.push("server-delete");
            }) as never);
            mockUnsubscribe.mockImplementation(async () => {
                callOrder.push("browser-unsubscribe");
                return true;
            });

            const push = usePush();
            const result = await push.unsubscribe();

            expect(result).toBe(true);
            expect(callOrder).toEqual(["server-delete", "browser-unsubscribe"]);
        });

        it("returns false on API failure", async () => {
            const mockSub = {
                endpoint: "https://push.example.com/sub/fail",
                unsubscribe: vi.fn(),
            } as unknown as PushSubscription;
            setupBrowserMocks({ existingSubscription: mockSub });
            vi.mocked(notificationsSubscriptionsList).mockRejectedValue(new Error("Network error"));

            const push = usePush();
            const result = await push.unsubscribe();

            expect(result).toBe(false);
        });
    });
});
