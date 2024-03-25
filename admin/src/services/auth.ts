import { type Ref, ref } from "vue";
import { useAPI } from "@/services/api";
import { ApiError, type SocialAuthURL, type UserData } from "@/api";

export type CurrentUserInfo = {
    firstName: string;
    lastName: string;
    email: string;
    permissions: number[];
    isSuperUser: boolean;
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

    function isLoggedIn(): boolean {
        return loggedIn.value;
    }

    async function login(username: string, password: string): Promise<boolean> {
        try {
            await api.auth.login({ username, password });
            await refreshStatus();
            return true;
        } catch (e) {
            // Log error if we got anything else than 401 error (expected on incorrect username + password
            if (e instanceof ApiError && e.status !== 401) {
                console.error(e);
            }
            return false;
        }
    }

    async function getSocialAuthURLs(): Promise<SocialAuthURL[]> {
        return api.auth.getSocialAuthUrls("/management");
    }

    async function tryFetchUserData(): Promise<UserData | undefined> {
        try {
            const result = await api.userInfo.userInfoList();
            return result.length > 0 ? result[0] : undefined;
        } catch (e) {
            return undefined;
        }
    }

    async function refreshStatus(): Promise<boolean> {
        const info = await tryFetchUserData();
        loggedIn.value = info !== undefined;
        userInfo.value = {
            firstName: info?.first_name || "",
            lastName: info?.last_name || "",
            email: info?.email || "",
            permissions: info?.user_permissions || [],
            isSuperUser: info?.is_superuser || false,
        };
        return loggedIn.value;
    }

    async function getUserData(): Promise<CurrentUserInfo> {
        return userInfo.value;
    }

    async function logout() {
        await api.auth.logout();
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
