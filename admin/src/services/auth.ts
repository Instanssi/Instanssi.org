import { type Ref, ref } from "vue";
import { useAPI } from "@/apis";

export type CurrentUserInfo = {
    firstName: string;
    lastName: string;
    email: string;
    permissions: string[];
    isSuperUser: boolean;
};

export type SocialAuthMethod = {
    method: string;
    url: string;
    name: string;
};

const loggedIn: Ref<boolean> = ref(false);
const userInfo: Ref<CurrentUserInfo> = ref({
    firstName: "",
    lastName: "",
    email: "",
    permissions: [],
    isSuperUser: false,
});

export function useAuth() {
    const api = useAPI();

    function isLoggedIn() {
        return loggedIn.value;
    }

    async function login(username: string, password: string) {
        const result = await api.auth.postLogin(username, password);
        if (result) {
            await refreshStatus();
        }
        return result;
    }

    async function getSocialAuthURLs(): Promise<SocialAuthMethod[]> {
        return await api.auth.getSocialAuthURLs("/management");
    }

    async function refreshStatus(): Promise<boolean> {
        const result = await api.auth.getCurrentUserInfo();
        loggedIn.value = result !== null;
        userInfo.value = {
            firstName: result?.first_name || "",
            lastName: result?.last_name || "",
            email: result?.email || "",
            permissions: result?.user_permissions || [],
            isSuperUser: result?.is_superuser || false,
        };
        return loggedIn.value;
    }

    async function getUserData(): Promise<CurrentUserInfo> {
        return userInfo.value;
    }

    async function logout() {
        await api.auth.postLogout();
        loggedIn.value = false;
        userInfo.value = {
            firstName: "",
            lastName: "",
            email: "",
            permissions: [],
            isSuperUser: false,
        };
    }

    return { isLoggedIn, login, logout, getSocialAuthURLs, refreshStatus, getUserData };
}
