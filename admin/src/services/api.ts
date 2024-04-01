import { useCookies } from "@vueuse/integrations/useCookies";

import { APIClient } from "@/api";
import { CustomAxiosHttpRequest } from "@/services/utils/axiosRequest";

export function useAPI() {
    const cookies = useCookies(["csrftoken"]);
    async function getHeaders() {
        return { "X-CSRFToken": cookies.get("csrftoken") };
    }

    return new APIClient({ HEADERS: getHeaders }, CustomAxiosHttpRequest);
}
