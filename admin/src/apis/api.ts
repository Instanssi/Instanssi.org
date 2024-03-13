import { useCookies } from "@vueuse/integrations/useCookies";

export type Qs = Record<string, string> | undefined;
type ResponseObj = { status: number; payload: any };

export class API {
    private readonly basePath: string;
    private readonly cookies;

    constructor(basePath: string = "/api/v1") {
        this.basePath = basePath;
        this.cookies = useCookies(["csrftoken"]);
    }

    protected makeUrl(path: string, query: Qs): string {
        const address = `${this.basePath}${path}`;
        if (query) {
            return address + "?" + new URLSearchParams(query);
        }
        return address;
    }

    protected async getJSON(path: string, query: Qs = undefined): Promise<ResponseObj> {
        const response = await fetch(this.makeUrl(path, query), {
            method: "GET",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
        });
        return { status: response.status, payload: await response.json() };
    }

    protected async postJSON(
        path: string,
        payload: object,
        query: Qs = undefined
    ): Promise<ResponseObj> {
        const response = await fetch(this.makeUrl(path, query), {
            method: "POST",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
                "X-CSRFToken": this.cookies.get("csrftoken"),
            },
            body: JSON.stringify(payload),
        });
        return { status: response.status, payload: await response.json() };
    }
}
