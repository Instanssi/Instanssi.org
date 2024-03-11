import { AuthAPI } from "@/apis/auth_api";

const apiBase = {
    auth: new AuthAPI(),
};

export function useAPI() {
    return apiBase;
}
