/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CompoEntry } from "../models/CompoEntry";
import type { CompoEntryRequest } from "../models/CompoEntryRequest";
import type { PaginatedCompoEntryList } from "../models/PaginatedCompoEntryList";
import type { PatchedCompoEntryRequest } from "../models/PatchedCompoEntryRequest";
import type { CancelablePromise } from "../core/CancelablePromise";
import type { BaseHttpRequest } from "../core/BaseHttpRequest";
export class UserCompoEntriesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @returns PaginatedCompoEntryList
     * @throws ApiError
     */
    public userCompoEntriesList(
        limit?: number,
        offset?: number,
        ordering?: string
    ): CancelablePromise<PaginatedCompoEntryList> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/user_compo_entries/",
            query: {
                limit: limit,
                offset: offset,
                ordering: ordering,
            },
        });
    }
    /**
     * @param formData
     * @returns CompoEntry
     * @throws ApiError
     */
    public userCompoEntriesCreate(formData: CompoEntryRequest): CancelablePromise<CompoEntry> {
        return this.httpRequest.request({
            method: "POST",
            url: "/api/v2/user_compo_entries/",
            formData: formData,
            mediaType: "multipart/form-data",
        });
    }
    /**
     * @param id
     * @returns CompoEntry
     * @throws ApiError
     */
    public userCompoEntriesRetrieve(id: string): CancelablePromise<CompoEntry> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/user_compo_entries/{id}/",
            path: {
                id: id,
            },
        });
    }
    /**
     * @param id
     * @param formData
     * @returns CompoEntry
     * @throws ApiError
     */
    public userCompoEntriesUpdate(
        id: string,
        formData: CompoEntryRequest
    ): CancelablePromise<CompoEntry> {
        return this.httpRequest.request({
            method: "PUT",
            url: "/api/v2/user_compo_entries/{id}/",
            path: {
                id: id,
            },
            formData: formData,
            mediaType: "multipart/form-data",
        });
    }
    /**
     * @param id
     * @param formData
     * @returns CompoEntry
     * @throws ApiError
     */
    public userCompoEntriesPartialUpdate(
        id: string,
        formData?: PatchedCompoEntryRequest
    ): CancelablePromise<CompoEntry> {
        return this.httpRequest.request({
            method: "PATCH",
            url: "/api/v2/user_compo_entries/{id}/",
            path: {
                id: id,
            },
            formData: formData,
            mediaType: "multipart/form-data",
        });
    }
    /**
     * @param id
     * @returns void
     * @throws ApiError
     */
    public userCompoEntriesDestroy(id: string): CancelablePromise<void> {
        return this.httpRequest.request({
            method: "DELETE",
            url: "/api/v2/user_compo_entries/{id}/",
            path: {
                id: id,
            },
        });
    }
}
