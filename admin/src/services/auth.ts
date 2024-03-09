import { ref } from "vue";

const loggedIn = ref(false);

export function useAuth() {
    function isLoggedIn() {
        return loggedIn.value;
    }

    async function login(username: string, password: string) {
        loggedIn.value = true;
        return true;
    }

    function logout() {
        loggedIn.value = false;
    }

    return { isLoggedIn, login, logout };
}
