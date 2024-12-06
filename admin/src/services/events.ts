import { type Ref, ref } from "vue";

import { type Event } from "@/api";
import * as api from "@/api";

const events: Ref<Event[]> = ref([]);

export function useEvents() {
    function getEvents(): Event[] {
        return events.value;
    }

    function getLatestEvent(): Event | null {
        const sorted = events.value.sort((a, b) => b.id - a.id);
        if (sorted.length > 0) {
            return sorted[0];
        }
        return null;
    }

    async function refreshEvents(): Promise<void> {
        const pages = await api.eventsList({ query: { limit: 1000 } });
        events.value = pages.data?.results || [];
    }

    return { getEvents, refreshEvents, getLatestEvent };
}
