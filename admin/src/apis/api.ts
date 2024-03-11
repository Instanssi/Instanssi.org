type Qs = Record<string, string> | undefined;
type ResponseObj = { status: number; payload: any };

export class API {
    private readonly basePath: string;

    constructor(basePath: string = "/api/v1") {
        this.basePath = basePath;
    }

    protected makeUrl(path: string, query: Record<string, string> | undefined): string {
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
            },
            body: JSON.stringify(payload),
        });
        return { status: response.status, payload: await response.json() };
    }
}
