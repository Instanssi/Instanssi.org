import axios from "axios";
import type { AxiosInstance } from "axios";

import { BaseHttpRequest, CancelablePromise } from "@/api";
import type { OpenAPIConfig } from "@/api";
import type { ApiRequestOptions } from "@/api/core/ApiRequestOptions";
import { request as __request } from "@/api/core/request";
import { errorResponseInterceptor } from "@/services/utils/interceptors";

export class CustomAxiosHttpRequest extends BaseHttpRequest {
    protected readonly axiosClient: AxiosInstance;

    constructor(config: OpenAPIConfig) {
        super(config);
        this.axiosClient = axios.create({
            xsrfCookieName: "csrftoken",
            xsrfHeaderName: "X-CSRFToken",
        });
        this.axiosClient.defaults.timeout = 5000;
        this.axiosClient.interceptors.response.use(null, errorResponseInterceptor);
    }

    public override request<T>(options: ApiRequestOptions): CancelablePromise<T> {
        return __request(this.config, options, this.axiosClient);
    }
}
