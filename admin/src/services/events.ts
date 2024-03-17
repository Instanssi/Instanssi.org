import { type Ref, ref } from "vue";
import { useAPI } from "@/apis";
import { type Event } from "@/apis/events_api";

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
        events.value = await api.events.getAllEvents();
    }

    return { getEvents, refreshEvents, getLatestEvent };
}
