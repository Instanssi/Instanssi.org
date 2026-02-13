declare const self: ServiceWorkerGlobalScope;

/** Service worker for Web Push notifications. */

const BASE_URL = import.meta.env.BASE_URL;

interface NotificationMessage {
    title?: string;
    body?: string;
    url?: string;
}

/**
 * Show a browser notification when the backend sends a Web Push message.
 *
 * The backend delivers notifications via Celery tasks using pywebpush (VAPID) to the browsers
 * service provider. Browser then receives that push event, and triggers this event.
 *
 * Expects the push payload to be JSON with optional `title`, `body`, and `url` fields.
 * Falls back to using the raw text as the notification body if JSON parsing fails.
 */
function onPush(event: PushEvent): void {
    if (!event.data) return;

    let data: NotificationMessage;
    try {
        data = event.data.json();
    } catch {
        data = { title: "Instanssi", body: event.data.text() };
    }

    const options: NotificationOptions = {
        body: data.body || "",
        icon: `${BASE_URL}favicon.png`,
        data: { url: data.url || BASE_URL },
    };

    event.waitUntil(self.registration.showNotification(data.title || "Instanssi", options));
}

/**
 * Handle a notification click by focusing an existing app window or opening a new one.
 *
 * If an app window is already open, it is focused and navigated to the notification's URL.
 * Otherwise a new window is opened.
 */
function onNotificationClick(event: NotificationEvent): void {
    event.notification.close();

    const url: string = event.notification.data?.url || BASE_URL;

    event.waitUntil(
        (async () => {
            const windowClients = await self.clients.matchAll({
                type: "window",
                includeUncontrolled: true,
            });
            for (const client of windowClients) {
                if (client.url.includes(BASE_URL) && "focus" in client) {
                    const windowClient = client as WindowClient;
                    await windowClient.focus();
                    await windowClient.navigate(url);
                    return;
                }
            }
            await self.clients.openWindow(url);
        })()
    );
}

self.addEventListener("push", onPush);
self.addEventListener("notificationclick", onNotificationClick);
