import { API } from "@/apis/api";

export type SocialAuthMethodsResponse = Array<{
    method: string;
    url: string;
    name: string;
}>;

export type CurrentUserInfoResponse = {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    user_permissions: string[];
    is_superuser: boolean;
};

export class AuthAPI extends API {
    public async getSocialAuthURLs(next: string): Promise<SocialAuthMethodsResponse> {
        const { payload } = await this.getJSON("/auth/social/begin/", { next });
        return payload;
    }

    public async postLogin(username: string, password: string): Promise<boolean> {
        const { status } = await this.postJSON("/auth/login/", { username, password });
        return status === 200;
    }

    public async getCurrentUserInfo(): Promise<CurrentUserInfoResponse | null> {
        const { status, payload } = await this.getJSON("/self/info/");
        return status === 200 ? payload : null;
    }

    public async postLogout() {
        await this.postJSON("/auth/logout/", {});
    }
}
