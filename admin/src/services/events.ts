import { type Ref, ref } from "vue";

import { type Event } from "@/api";
import * as api from "@/api";

const events: Ref<Event[]> = ref([]);

export function useEvents() {
    function getEvents(): Event[] {
        return events.value;
    }

    function getLatestEvent(): Event | null {
        return events.value[0] ?? null;
    }

    async function refreshEvents(): Promise<void> {
        const pages = await api.adminEventsList({ query: { limit: 1000, ordering: "-id" } });
        events.value = pages.data?.results || [];
    }

    function getEventById(id: number): Event | null {
        return events.value.find((e) => e.id === id) ?? null;
    }

    return { getEvents, refreshEvents, getLatestEvent, getEventById };
}
