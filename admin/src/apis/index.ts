import { AuthAPI } from "@/apis/auth_api";
import { EventsAPI } from "@/apis/events_api";

const apiBase = {
    auth: new AuthAPI(),
    events: new EventsAPI(),
};

export function useAPI() {
    return apiBase;
}
