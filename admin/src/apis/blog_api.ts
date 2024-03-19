import { API, type Filters, type Limit, type Offset, type OrderBy, type Search } from "@/apis/api";
import type { Pagination } from "@/apis/types";

export type BlogPost = {
    id: number;
    user: number;
    title: string;
    date: Date;
    text: string;
    public: boolean;
};

export class BlogAPI extends API {
    public async getBlogEntries(
        filters: Filters,
        offset: Offset,
        limit: Limit,
        search: Search,
        orderBy: OrderBy
    ): Promise<Pagination<BlogPost>> {
        const query = this.makeQs(limit, offset, search, filters, orderBy);
        const { payload } = await this.getJSON("/blog/", query);
        payload.results = payload.results.map((item: Record<string, any>) => ({
            ...item,
            date: new Date(item.date),
        }));
        return payload;
    }

    public async postBlogEntry(
        event: number,
        title: string,
        text: string,
        isPublic: boolean
    ): Promise<void> {
        await this.postJSON("/blog/", { title, text, event, public: isPublic });
    }

    public async deleteBlogEntry(id: number): Promise<void> {
        await this.delete(`/blog/${id}/`);
    }

    public async patchBlogEntry(
        id: number,
        title: string,
        text: string,
        isPublic: boolean
    ): Promise<void> {
        await this.patchJSON(`/blog/${id}/`, { title, text, public: isPublic });
    }
}
