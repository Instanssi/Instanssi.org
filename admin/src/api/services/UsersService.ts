/* generated using openapi-typescript-codegen -- do not edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { BaseHttpRequest } from "../core/BaseHttpRequest";
import type { CancelablePromise } from "../core/CancelablePromise";
import type { PaginatedUserList } from "../models/PaginatedUserList";
import type { PatchedUserRequest } from "../models/PatchedUserRequest";
import type { User } from "../models/User";
import type { UserRequest } from "../models/UserRequest";

export class UsersService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * @param email
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @param username
     * @returns PaginatedUserList
     * @throws ApiError
     */
    public usersList(
        email?: string,
        limit?: number,
        offset?: number,
        ordering?: string,
        username?: string
    ): CancelablePromise<PaginatedUserList> {
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
     * @returns User
     * @throws ApiError
     */
    public usersCreate(requestBody: UserRequest): CancelablePromise<User> {
        return this.httpRequest.request({
            method: "POST",
            url: "/api/v2/users/",
            body: requestBody,
            mediaType: "application/json",
        });
    }
    /**
     * @param id A unique integer value identifying this käyttäjä.
     * @returns User
     * @throws ApiError
     */
    public usersRetrieve(id: number): CancelablePromise<User> {
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
     * @returns User
     * @throws ApiError
     */
    public usersUpdate(id: number, requestBody: UserRequest): CancelablePromise<User> {
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
     * @returns User
     * @throws ApiError
     */
    public usersPartialUpdate(
        id: number,
        requestBody?: PatchedUserRequest
    ): CancelablePromise<User> {
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
