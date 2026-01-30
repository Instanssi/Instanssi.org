import { client } from "@/api/client.gen.ts";
import { errorResponseInterceptor } from "@/services/utils/interceptors";

export function setupClient() {
    client.setConfig({
        throwOnError: true,
        xsrfCookieName: "csrftoken",
        xsrfHeaderName: "X-CSRFToken",
        timeout: 5000,
    });
    client.instance.interceptors.response.use(null, errorResponseInterceptor);
}
