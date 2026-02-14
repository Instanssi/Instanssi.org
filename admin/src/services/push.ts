import {
    notificationsSubscriptionsCreate,
    notificationsSubscriptionsDestroy,
    notificationsSubscriptionsList,
    publicNotificationsVapidKeyRetrieve,
} from "@/api";
import { ref, type Ref } from "vue";

export type PushState = "unsupported" | "default" | "granted" | "denied";

// TODO: Replace with Uint8Array.fromBase64(s, { alphabet: "base64url" }) when ES2025 is
//       available in TypeScript's lib and the test runner (Node.js / happy-dom).
export function urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; i++) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

/**
 * Composable for managing Web Push notification subscriptions.
 *
 * Handles service worker registration and browser push subscription lifecycle.
 */
export function usePush() {
    /** Current browser push permission state. */
    const pushState: Ref<PushState> = ref("default");
    /** Whether the browser has an active push subscription. */
    const subscribed: Ref<boolean> = ref(false);
    /** Whether a subscribe/unsubscribe operation is in progress. */
    const loading: Ref<boolean> = ref(false);

    /** Wait for the service worker (registered by vite-plugin-pwa) and check push status. */
    async function init(): Promise<void> {
        if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
            pushState.value = "unsupported";
            return;
        }

        pushState.value = Notification.permission as PushState;
        await checkSubscription();
    }

    /** Check if the browser currently has an active push subscription. */
    async function checkSubscription(): Promise<void> {
        try {
            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.getSubscription();
            subscribed.value = subscription !== null;
            if (subscribed.value) {
                pushState.value = "granted";
            }
        } catch (e) {
            console.error("Failed to check push subscription:", e);
        }
    }

    /**
     * Subscribe to push notifications.
     *
     * Fetches the server's VAPID public key, requests browser push permission,
     * creates a push subscription, and registers it with the backend.
     * @returns true if subscription succeeded, false otherwise.
     */
    async function subscribe(): Promise<boolean> {
        loading.value = true;
        try {
            const { data: vapidData } = await publicNotificationsVapidKeyRetrieve();
            const vapidPublicKey = (vapidData?.vapid_public_key ?? "").trim();

            if (!vapidPublicKey) {
                console.error("VAPID public key not configured on server");
                return false;
            }

            const registration = await navigator.serviceWorker.ready;
            const applicationServerKey = urlBase64ToUint8Array(vapidPublicKey);
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: applicationServerKey as BufferSource,
            });

            const key = subscription.getKey("p256dh");
            const auth = subscription.getKey("auth");
            if (!key || !auth) {
                console.error("Failed to get subscription keys");
                return false;
            }

            const p256dh = btoa(String.fromCharCode(...new Uint8Array(key)));
            const authKey = btoa(String.fromCharCode(...new Uint8Array(auth)));

            await notificationsSubscriptionsCreate({
                body: { endpoint: subscription.endpoint, p256dh: p256dh, auth: authKey },
            });

            subscribed.value = true;
            pushState.value = "granted";
            return true;
        } catch (e) {
            console.error("Failed to subscribe to push:", e);
            if (Notification.permission === "denied") {
                pushState.value = "denied";
            }
            return false;
        } finally {
            loading.value = false;
        }
    }

    /**
     * Unsubscribe from push notifications.
     *
     * Removes the browser push subscription and deletes only the matching
     * server-side subscription (identified by endpoint), preserving
     * subscriptions from other browsers/devices.
     * @returns true if unsubscription succeeded, false otherwise.
     */
    async function unsubscribe(): Promise<boolean> {
        loading.value = true;
        try {
            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.getSubscription();
            if (subscription) {
                // Delete server-side first so a failure doesn't orphan the record
                // (the browser subscription would still work and the user can retry).
                const { data: subs } = await notificationsSubscriptionsList();
                const match = (subs ?? []).find((sub) => sub.endpoint === subscription.endpoint);
                if (match) {
                    await notificationsSubscriptionsDestroy({ path: { id: match.id } });
                }

                await subscription.unsubscribe();
            }

            subscribed.value = false;
            return true;
        } catch (e) {
            console.error("Failed to unsubscribe from push:", e);
            return false;
        } finally {
            loading.value = false;
        }
    }

    return {
        pushState,
        subscribed,
        loading,
        init,
        subscribe,
        unsubscribe,
    };
}
