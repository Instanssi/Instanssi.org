import { client, configureClient } from "@instanssi/api";

import { errorResponseInterceptor } from "@/services/utils/interceptors";

export function setupClient() {
    configureClient(client, { timeout: 5000 });
    client.interceptors.error.use(errorResponseInterceptor);
}
