import { client } from "@/api";
import { errorResponseInterceptor } from "@/services/utils/interceptors";

export function setupClient() {
    client.instance.defaults.xsrfCookieName = "csrftoken";
    client.instance.defaults.xsrfHeaderName = "X-CSRFToken";
    client.instance.defaults.timeout = 5000;
    client.instance.interceptors.request.use(null, errorResponseInterceptor);
}
