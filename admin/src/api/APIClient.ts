import { AxiosHttpRequest } from "./core/AxiosHttpRequest";
import type { BaseHttpRequest } from "./core/BaseHttpRequest";
import type { OpenAPIConfig } from "./core/OpenAPI";
import { Interceptors } from "./core/OpenAPI";
import { AuthService } from "./services.gen";
import { BlogEntriesService } from "./services.gen";
import { EventsService } from "./services.gen";
import { UserCompoEntriesService } from "./services.gen";
import { UserInfoService } from "./services.gen";
import { UsersService } from "./services.gen";

type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;

export class APIClient {
    public readonly auth: AuthService;
    public readonly blogEntries: BlogEntriesService;
    public readonly events: EventsService;
    public readonly userCompoEntries: UserCompoEntriesService;
    public readonly userInfo: UserInfoService;
    public readonly users: UsersService;

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
            interceptors: {
                request: new Interceptors(),
                response: new Interceptors(),
            },
        });

        this.auth = new AuthService(this.request);
        this.blogEntries = new BlogEntriesService(this.request);
        this.events = new EventsService(this.request);
        this.userCompoEntries = new UserCompoEntriesService(this.request);
        this.userInfo = new UserInfoService(this.request);
        this.users = new UsersService(this.request);
    }
}
