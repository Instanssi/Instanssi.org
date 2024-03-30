/* generated using openapi-typescript-codegen -- do not edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { BaseHttpRequest } from "../core/BaseHttpRequest";
import type { CancelablePromise } from "../core/CancelablePromise";
import type { BlogEntry } from "../models/BlogEntry";
import type { BlogEntryRequest } from "../models/BlogEntryRequest";
import type { PaginatedBlogEntryList } from "../models/PaginatedBlogEntryList";
import type { PatchedBlogEntryRequest } from "../models/PatchedBlogEntryRequest";

export class BlogEntriesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * @param event
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @param search A search term.
     * @param user
     * @returns PaginatedBlogEntryList
     * @throws ApiError
     */
    public blogEntriesList(
        event?: number,
        limit?: number,
        offset?: number,
        ordering?: string,
        search?: string,
        user?: number
    ): CancelablePromise<PaginatedBlogEntryList> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/blog_entries/",
            query: {
                event: event,
                limit: limit,
                offset: offset,
                ordering: ordering,
                search: search,
                user: user,
            },
        });
    }
    /**
     * @param requestBody
     * @returns BlogEntry
     * @throws ApiError
     */
    public blogEntriesCreate(requestBody: BlogEntryRequest): CancelablePromise<BlogEntry> {
        return this.httpRequest.request({
            method: "POST",
            url: "/api/v2/blog_entries/",
            body: requestBody,
            mediaType: "application/json",
        });
    }
    /**
     * @param id A unique integer value identifying this entry.
     * @returns BlogEntry
     * @throws ApiError
     */
    public blogEntriesRetrieve(id: number): CancelablePromise<BlogEntry> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/blog_entries/{id}/",
            path: {
                id: id,
            },
        });
    }
    /**
     * @param id A unique integer value identifying this entry.
     * @param requestBody
     * @returns BlogEntry
     * @throws ApiError
     */
    public blogEntriesUpdate(
        id: number,
        requestBody: BlogEntryRequest
    ): CancelablePromise<BlogEntry> {
        return this.httpRequest.request({
            method: "PUT",
            url: "/api/v2/blog_entries/{id}/",
            path: {
                id: id,
            },
            body: requestBody,
            mediaType: "application/json",
        });
    }
    /**
     * @param id A unique integer value identifying this entry.
     * @param requestBody
     * @returns BlogEntry
     * @throws ApiError
     */
    public blogEntriesPartialUpdate(
        id: number,
        requestBody?: PatchedBlogEntryRequest
    ): CancelablePromise<BlogEntry> {
        return this.httpRequest.request({
            method: "PATCH",
            url: "/api/v2/blog_entries/{id}/",
            path: {
                id: id,
            },
            body: requestBody,
            mediaType: "application/json",
        });
    }
    /**
     * @param id A unique integer value identifying this entry.
     * @returns void
     * @throws ApiError
     */
    public blogEntriesDestroy(id: number): CancelablePromise<void> {
        return this.httpRequest.request({
            method: "DELETE",
            url: "/api/v2/blog_entries/{id}/",
            path: {
                id: id,
            },
        });
    }
}
