import { useCookies } from "@vueuse/integrations/useCookies";
import { boolean } from "yup";

export type Qs = Record<string, string> | undefined;
type ResponseObj = { status: number; payload: any };
export type OrderField = {
    key: string;
    order: "asc" | "desc";
};
export type OrderBy = OrderField[] | undefined | null;
export type Filters = { [key: string]: any } | undefined | null;
export type Limit = number | undefined | null;
export type Offset = number | undefined | null;
export type Search = string | undefined | null;

export class API {
    private readonly basePath: string;
    private readonly cookies;

    constructor(basePath: string = "/api/v1") {
        this.basePath = basePath;
        this.cookies = useCookies(["csrftoken"]);
    }

    /**
     * Form an URL from base path and query string
     * @param path Any URL without query params
     * @param query Query params object (See: makeQs)
     * @protected
     */
    protected makeUrl(path: string, query: Qs): string {
        const address = `${this.basePath}${path}`;
        if (query) {
            return address + "?" + new URLSearchParams(query);
        }
        return address;
    }

    /**
     * Accept all the standard query arguments and handle them into parameter object.
     * @param limit Limit returned objects
     * @param offset Start returning objects from entry
     * @param search Search by arbitrary string
     * @param filters Filter by field
     * @param orderBy Order by field
     * @protected
     */
    protected makeQs(
        limit: Limit,
        offset: Offset,
        search: Search,
        filters: Filters,
        orderBy: OrderBy
    ): Qs {
        const output: Qs = {};
        for (const [key, value] of Object.entries(filters ?? {})) {
            if (value === undefined || value == null) continue;
            if (value instanceof boolean) {
                output[key] = value ? "True" : "False";
            } else {
                output[key] = value.toString();
            }
        }
        if (limit !== undefined && limit != null) {
            output["limit"] = limit.toString();
        }
        if (offset !== undefined && offset != null && offset !== 0) {
            output["offset"] = offset.toString();
        }
        if (search !== undefined && search != null && search !== "") {
            output["search"] = search.toString();
        }
        if (orderBy !== undefined && orderBy != null && orderBy.length > 0) {
            if (orderBy.length != 1) {
                throw Error("Multiple ordering options are not supported!");
            }
            const item = orderBy[0];
            if (item.order === "desc") {
                output["ordering"] = `${item.key}`;
            } else {
                output["ordering"] = `-${item.key}`;
            }
        }
        return output;
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

    protected async patchJSON(
        path: string,
        payload: object,
        query: Qs = undefined
    ): Promise<ResponseObj> {
        const response = await fetch(this.makeUrl(path, query), {
            method: "PATCH",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
                "X-CSRFToken": this.cookies.get("csrftoken"),
            },
            body: JSON.stringify(payload),
        });
        return { status: response.status, payload: await response.json() };
    }

    protected async delete(path: string): Promise<ResponseObj> {
        const response = await fetch(this.makeUrl(path, {}), {
            method: "DELETE",
            headers: {
                "X-CSRFToken": this.cookies.get("csrftoken"),
            },
        });
        return { status: response.status, payload: null };
    }
}
