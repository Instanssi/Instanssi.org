import type { CurrentUserInfoResponse, SocialAuthMethodsResponse } from "@/apis/types";
import { API } from "@/apis/api";

export class AuthAPI extends API {
    public async getSocialAuthURLs(next: string): Promise<SocialAuthMethodsResponse> {
        const { payload } = await this.getJSON("/auth/social_login/begin/", { next });
        return payload;
    }

    public async postLogin(username: string, password: string): Promise<boolean> {
        const { status } = await this.postJSON("/auth/login/", { username, password });
        return status === 200;
    }

    public async getCurrentUserInfo(): Promise<CurrentUserInfoResponse | null> {
        const { status, payload } = await this.getJSON("/auth/user_info/");
        return status === 200 ? payload : null;
    }

    public async postLogout() {
        await this.postJSON("/auth/logout/", {});
    }
}
