import { API } from "@/apis/api";

export type Event = {
    id: number;
    name: string;
    date: Date;
    archived: boolean;
    mainurl: string;
};

export class EventsAPI extends API {
    public async getAllEvents(): Promise<Event[]> {
        const { payload } = await this.getJSON("/admin/events/");
        payload.date = new Date(payload.date);
        return payload;
    }
}
