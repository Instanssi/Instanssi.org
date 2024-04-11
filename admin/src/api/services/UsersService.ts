/* generated using openapi-typescript-codegen -- do not edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { BaseHttpRequest } from "../core/BaseHttpRequest";
import type { CancelablePromise } from "../core/CancelablePromise";
import type { PaginatedUserInfoList } from "../models/PaginatedUserInfoList";
import type { PatchedUserInfoRequest } from "../models/PatchedUserInfoRequest";
import type { UserInfo } from "../models/UserInfo";
import type { UserInfoRequest } from "../models/UserInfoRequest";

export class UsersService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * @param email
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @param username
     * @returns PaginatedUserInfoList
     * @throws ApiError
     */
    public usersList(
        email?: string,
        limit?: number,
        offset?: number,
        ordering?: string,
        username?: string
    ): CancelablePromise<PaginatedUserInfoList> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/users/",
            query: {
                email: email,
                limit: limit,
                offset: offset,
                ordering: ordering,
                username: username,
            },
        });
    }
    /**
     * @param requestBody
     * @returns UserInfo
     * @throws ApiError
     */
    public usersCreate(requestBody: UserInfoRequest): CancelablePromise<UserInfo> {
        return this.httpRequest.request({
            method: "POST",
            url: "/api/v2/users/",
            body: requestBody,
            mediaType: "application/json",
        });
    }
    /**
     * @param id A unique integer value identifying this käyttäjä.
     * @returns UserInfo
     * @throws ApiError
     */
    public usersRetrieve(id: number): CancelablePromise<UserInfo> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/users/{id}/",
            path: {
                id: id,
            },
        });
    }
    /**
     * @param id A unique integer value identifying this käyttäjä.
     * @param requestBody
     * @returns UserInfo
     * @throws ApiError
     */
    public usersUpdate(id: number, requestBody: UserInfoRequest): CancelablePromise<UserInfo> {
        return this.httpRequest.request({
            method: "PUT",
            url: "/api/v2/users/{id}/",
            path: {
                id: id,
            },
            body: requestBody,
            mediaType: "application/json",
        });
    }
    /**
     * @param id A unique integer value identifying this käyttäjä.
     * @param requestBody
     * @returns UserInfo
     * @throws ApiError
     */
    public usersPartialUpdate(
        id: number,
        requestBody?: PatchedUserInfoRequest
    ): CancelablePromise<UserInfo> {
        return this.httpRequest.request({
            method: "PATCH",
            url: "/api/v2/users/{id}/",
            path: {
                id: id,
            },
            body: requestBody,
            mediaType: "application/json",
        });
    }
    /**
     * @param id A unique integer value identifying this käyttäjä.
     * @returns void
     * @throws ApiError
     */
    public usersDestroy(id: number): CancelablePromise<void> {
        return this.httpRequest.request({
            method: "DELETE",
            url: "/api/v2/users/{id}/",
            path: {
                id: id,
            },
        });
    }
}
