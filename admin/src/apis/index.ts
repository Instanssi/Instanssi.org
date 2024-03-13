import { AuthAPI } from "@/apis/auth_api";
import { BlogAPI } from "@/apis/blog_api";
import { EventsAPI } from "@/apis/events_api";

const apiBase = {
    auth: new AuthAPI(),
    blog: new BlogAPI(),
    events: new EventsAPI(),
};

export function useAPI() {
    return apiBase;
}
