import { type Ref, ref } from "vue";

import { type Event } from "@/api";
import { useAPI } from "@/services/api";

const events: Ref<Event[]> = ref([]);

export function useEvents() {
    const api = useAPI();

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
        const pages = await api.events.eventsList({ limit: 1000 });
        events.value = pages.results;
    }

    return { getEvents, refreshEvents, getLatestEvent };
}
