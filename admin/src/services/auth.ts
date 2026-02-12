import { type Ref, ref } from "vue";

import * as api from "@/api";
import type { SocialAuthUrl, UserInfo } from "@/api";
import { isSupportedLocale, setLocale, type SupportedLocale } from "@/i18n";

export type CurrentUserInfo = {
    id: number;
    firstName: string;
    lastName: string;
    email: string;
    permissions: Set<string>;
    isSuperUser: boolean;
    language: string;
};

const loggedIn: Ref<boolean> = ref(false);
const userInfo: Ref<CurrentUserInfo> = ref({
    id: 0,
    firstName: "",
    lastName: "",
    email: "",
    permissions: new Set(),
    isSuperUser: false,
    language: "",
});

type PermissionType = "add" | "change" | "delete" | "view";

export enum PermissionTarget {
    AUTH_TOKEN = "authtoken",
    LOG_ENTRY = "logentry",
    UPLOADED_FILE = "uploadedfile",
    OTHER_VIDEO = "othervideo",
    OTHER_VIDEO_CATEGORY = "othervideocategory",
    BLOG_ENTRY = "blogentry",
    PROGRAMME_EVENT = "programmeevent",
    ALTERNATE_ENTRY_FILE = "alternateentryfile",
    COMPETITION = "competition",
    COMPETITION_PARTICIPATION = "competitionparticipation",
    COMPO = "compo",
    ENTRY = "entry",
    EVENT = "event",
    TICKET_VOTE_CODE = "ticketvotecode",
    VOTE = "vote",
    VOTE_CODE_REQUEST = "votecoderequest",
    VOTE_GROUP = "votegroup",
    RECEIPT = "receipt",
    STORE_ITEM = "storeitem",
    STORE_ITEM_VARIANT = "storeitemvariant",
    STORE_TRANSACTION = "storetransaction",
    STORE_TRANSACTION_EVENT = "storetransactionevent",
    TRANSACTION_ITEM = "transactionitem",
    USER = "user",
}

export function useAuth() {
    function isLoggedIn(): boolean {
        return loggedIn.value;
    }

    async function login(username: string, password: string): Promise<boolean> {
        const response = await api.login({ body: { username, password } });
        if (response.status === 200) {
            await refreshStatus();
            return true;
        }
        return false;
    }

    async function getSocialAuthURLs(): Promise<SocialAuthUrl[]> {
        const value = await api.getSocialAuthUrls({ query: { next: "/management" } });
        return value.data ?? [];
    }

    async function tryFetchUserData(): Promise<UserInfo | undefined> {
        try {
            const result = await api.userInfoRetrieve();
            if (result.data === undefined) return undefined;
            return result.data;
        } catch {
            return undefined;
        }
    }

    async function refreshStatus(): Promise<boolean> {
        const info = await tryFetchUserData();
        loggedIn.value = info !== undefined;
        userInfo.value = {
            id: info?.id || 0,
            firstName: info?.first_name || "",
            lastName: info?.last_name || "",
            email: info?.email || "",
            permissions: new Set(info?.user_permissions || []),
            isSuperUser: info?.is_superuser || false,
            language: info?.language || "",
        };
        if (info?.language && isSupportedLocale(info.language)) {
            setLocale(info.language);
        }
        return loggedIn.value;
    }

    async function updateLanguage(locale: SupportedLocale): Promise<void> {
        setLocale(locale);
        if (loggedIn.value && userInfo.value.id) {
            await api.userInfoPartialUpdate({ body: { language: locale } });
            userInfo.value = { ...userInfo.value, language: locale };
        }
    }

    function hasPermission(type: PermissionType, target: PermissionTarget): boolean {
        if (!userInfo.value) return false;
        if (userInfo.value.isSuperUser) return true;
        const permission = `${type}_${target.toString()}`;
        return userInfo.value.permissions.has(permission);
    }

    function canView(name: PermissionTarget): boolean {
        return hasPermission("view", name);
    }

    function canChange(name: PermissionTarget): boolean {
        return hasPermission("change", name);
    }

    function canDelete(name: PermissionTarget): boolean {
        return hasPermission("delete", name);
    }

    function canAdd(name: PermissionTarget): boolean {
        return hasPermission("add", name);
    }

    function isSuperUser(): boolean {
        return userInfo.value.isSuperUser;
    }

    async function getUserData(): Promise<CurrentUserInfo> {
        return userInfo.value;
    }

    async function logout() {
        await api.logout();
        loggedIn.value = false;
        userInfo.value = {
            id: 0,
            firstName: "",
            lastName: "",
            email: "",
            permissions: new Set(),
            isSuperUser: false,
            language: "",
        };
    }

    return {
        isLoggedIn,
        isSuperUser,
        login,
        logout,
        getSocialAuthURLs,
        refreshStatus,
        getUserData,
        updateLanguage,
        canView,
        canChange,
        canDelete,
        canAdd,
        hasPermission,
    };
}
