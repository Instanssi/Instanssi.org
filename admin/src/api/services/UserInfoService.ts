/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserInfo } from "../models/UserInfo";
import type { CancelablePromise } from "../core/CancelablePromise";
import type { BaseHttpRequest } from "../core/BaseHttpRequest";
export class UserInfoService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * @returns UserInfo
     * @throws ApiError
     */
    public userInfo(): CancelablePromise<Array<UserInfo>> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/user_info/",
        });
    }
}
