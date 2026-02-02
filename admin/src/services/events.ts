import { type Ref, ref } from "vue";

import { type Event } from "@/api";
import * as api from "@/api";

const events: Ref<Event[]> = ref([]);

/**
 * Sort events by date (newest first), with hidden events at the end.
 */
function sortEvents(eventList: Event[]): Event[] {
    return [...eventList].sort((a, b) => {
        if (a.hidden !== b.hidden) {
            return a.hidden ? 1 : -1;
        }
        return b.date.localeCompare(a.date);
    });
}

export function useEvents() {
    function getEvents(): Event[] {
        return events.value;
    }

    function getLatestEvent(): Event | null {
        // Return the first non-hidden event, or the first event if all are hidden
        return events.value.find((e) => !e.hidden) ?? events.value[0] ?? null;
    }

    async function refreshEvents(): Promise<void> {
        const pages = await api.adminEventsList({ query: { limit: 1000, ordering: "-date" } });
        events.value = sortEvents(pages.data?.results || []);
    }

    function getEventById(id: number): Event | null {
        return events.value.find((e) => e.id === id) ?? null;
    }

    return { getEvents, refreshEvents, getLatestEvent, getEventById };
}
