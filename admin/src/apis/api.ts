import type { SocialAuthUrls } from "@/apis/types";

type Qs = Record<string, string> | undefined;
type ResponseObj = { status: number; payload: any };

class API {
    private readonly basePath: string;

    constructor(basePath: string = "/api/v1") {
        this.basePath = basePath;
    }

    private makeUrl(path: string, query: Record<string, string> | undefined): string {
        const address = `${this.basePath}${path}`;
        if (query) {
            return address + "?" + new URLSearchParams(query);
        }
        return address;
    }

    private async getJSON(path: string, query: Qs = undefined): Promise<ResponseObj> {
        const response = await fetch(this.makeUrl(path, query), {
            method: "GET",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
        });
        return { status: response.status, payload: await response.json() };
    }

    private async postJSON(
        path: string,
        payload: object,
        query: Qs = undefined
    ): Promise<ResponseObj> {
        const response = await fetch(this.makeUrl(path, query), {
            method: "POST",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });
        return { status: response.status, payload: await response.json() };
    }

    public async getSocialAuthURLs(next: string): Promise<SocialAuthUrls> {
        const { payload } = await this.getJSON("/auth/social_login/begin/", { next });
        return payload;
    }

    public async postLogin(username: string, password: string): Promise<boolean> {
        const { status } = await this.postJSON("/auth/login/", { username, password });
        return status === 200;
    }
}

export const api = new API();
