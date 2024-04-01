/* generated using openapi-typescript-codegen -- do not edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { BaseHttpRequest } from "../core/BaseHttpRequest";
import type { CancelablePromise } from "../core/CancelablePromise";
import type { Event } from "../models/Event";
import type { EventRequest } from "../models/EventRequest";
import type { PaginatedEventList } from "../models/PaginatedEventList";
import type { PatchedEventRequest } from "../models/PatchedEventRequest";

export class EventsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * @param limit Number of results to return per page.
     * @param name
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @returns PaginatedEventList
     * @throws ApiError
     */
    public eventsList(
        limit?: number,
        name?: string,
        offset?: number,
        ordering?: string
    ): CancelablePromise<PaginatedEventList> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/events/",
            query: {
                limit: limit,
                name: name,
                offset: offset,
                ordering: ordering,
            },
        });
    }
    /**
     * @param requestBody
     * @returns Event
     * @throws ApiError
     */
    public eventsCreate(requestBody: EventRequest): CancelablePromise<Event> {
        return this.httpRequest.request({
            method: "POST",
            url: "/api/v2/events/",
            body: requestBody,
            mediaType: "application/json",
        });
    }
    /**
     * @param id A unique integer value identifying this tapahtuma.
     * @returns Event
     * @throws ApiError
     */
    public eventsRetrieve(id: number): CancelablePromise<Event> {
        return this.httpRequest.request({
            method: "GET",
            url: "/api/v2/events/{id}/",
            path: {
                id: id,
            },
        });
    }
    /**
     * @param id A unique integer value identifying this tapahtuma.
     * @param requestBody
     * @returns Event
     * @throws ApiError
     */
    public eventsUpdate(id: number, requestBody: EventRequest): CancelablePromise<Event> {
        return this.httpRequest.request({
            method: "PUT",
            url: "/api/v2/events/{id}/",
            path: {
                id: id,
            },
            body: requestBody,
            mediaType: "application/json",
        });
    }
    /**
     * @param id A unique integer value identifying this tapahtuma.
     * @param requestBody
     * @returns Event
     * @throws ApiError
     */
    public eventsPartialUpdate(
        id: number,
        requestBody?: PatchedEventRequest
    ): CancelablePromise<Event> {
        return this.httpRequest.request({
            method: "PATCH",
            url: "/api/v2/events/{id}/",
            path: {
                id: id,
            },
            body: requestBody,
            mediaType: "application/json",
        });
    }
    /**
     * @param id A unique integer value identifying this tapahtuma.
     * @returns void
     * @throws ApiError
     */
    public eventsDestroy(id: number): CancelablePromise<void> {
        return this.httpRequest.request({
            method: "DELETE",
            url: "/api/v2/events/{id}/",
            path: {
                id: id,
            },
        });
    }
}
