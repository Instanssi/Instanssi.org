/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserData } from "../models/UserData";
import type { CancelablePromise } from "../core/CancelablePromise";
import type { BaseHttpRequest } from "../core/BaseHttpRequest";
export class UserInfoService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * @returns UserData
     * @throws ApiError
     */
    public userInfoList(): CancelablePromise<Array<UserData>> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/user_info/",
        });
    }
    /**
     * @param id A unique integer value identifying this käyttäjä.
     * @returns UserData
     * @throws ApiError
     */
    public userInfoRetrieve(id: number): CancelablePromise<UserData> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/user_info/{id}/",
            path: {
                id: id,
            },
        });
    }
}
