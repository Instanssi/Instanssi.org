import { ref } from "vue";
import { api } from "@/apis/api";

const loggedIn = ref(false);

export function useAuth() {
    function isLoggedIn() {
        return loggedIn.value;
    }

    async function login(username: string, password: string) {
        const result = await api.postLogin(username, password);
        loggedIn.value = result;
        return result;
    }

    async function getSocialAuthURLs() {
        return await api.getSocialAuthURLs("/management");
    }

    function logout() {
        loggedIn.value = false;
    }

    return { isLoggedIn, login, logout, getSocialAuthURLs };
}
