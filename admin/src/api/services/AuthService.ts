/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SocialAuthURL } from "../models/SocialAuthURL";
import type { UserLoginRequest } from "../models/UserLoginRequest";
import type { CancelablePromise } from "../core/CancelablePromise";
import type { BaseHttpRequest } from "../core/BaseHttpRequest";
export class AuthService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * @param requestBody
     * @returns void
     * @throws ApiError
     */
    public login(requestBody: UserLoginRequest): CancelablePromise<void> {
        return this.httpRequest.request({
            method: "POST",
            url: "/api/v2/auth/login/",
            body: requestBody,
            mediaType: "application/json",
            errors: {
                400: `No response body`,
                401: `No response body`,
            },
        });
    }
    /**
     * @returns void
     * @throws ApiError
     */
    public logout(): CancelablePromise<void> {
        return this.httpRequest.request({
            method: "POST",
            url: "/api/v2/auth/logout/",
        });
    }
    /**
     * Returns a list of URLs that can be used to begin a social authentication process.
     * @param next
     * @returns SocialAuthURL
     * @throws ApiError
     */
    public getSocialAuthUrls(next?: string): CancelablePromise<Array<SocialAuthURL>> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/auth/social_urls/",
            query: {
                next: next,
            },
        });
    }
}
