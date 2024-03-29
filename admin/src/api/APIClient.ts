/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from "./core/BaseHttpRequest";
import type { OpenAPIConfig } from "./core/OpenAPI";
import { AxiosHttpRequest } from "./core/AxiosHttpRequest";
import { AuthService } from "./services/AuthService";
import { BlogEntriesService } from "./services/BlogEntriesService";
import { EventsService } from "./services/EventsService";
import { UserCompoEntriesService } from "./services/UserCompoEntriesService";
import { UserInfoService } from "./services/UserInfoService";
type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;
export class APIClient {
    public readonly auth: AuthService;
    public readonly blogEntries: BlogEntriesService;
    public readonly events: EventsService;
    public readonly userCompoEntries: UserCompoEntriesService;
    public readonly userInfo: UserInfoService;
    public readonly request: BaseHttpRequest;
    constructor(
        config?: Partial<OpenAPIConfig>,
        HttpRequest: HttpRequestConstructor = AxiosHttpRequest
    ) {
        this.request = new HttpRequest({
            BASE: config?.BASE ?? "",
            VERSION: config?.VERSION ?? "2.0.0",
            WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
            CREDENTIALS: config?.CREDENTIALS ?? "include",
            TOKEN: config?.TOKEN,
            USERNAME: config?.USERNAME,
            PASSWORD: config?.PASSWORD,
            HEADERS: config?.HEADERS,
            ENCODE_PATH: config?.ENCODE_PATH,
        });
        this.auth = new AuthService(this.request);
        this.blogEntries = new BlogEntriesService(this.request);
        this.events = new EventsService(this.request);
        this.userCompoEntries = new UserCompoEntriesService(this.request);
        this.userInfo = new UserInfoService(this.request);
    }
}
