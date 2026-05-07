import qs from 'qs';
import Cookies from 'cookies-js';
import { observable, action } from 'mobx';

import { PrimaryKey } from 'src/api/interfaces';
import globalState from 'src/state';

/**
 * API state tracking.
 */
export const apiState = observable({
    /** Requests in progress. */
    requests: 0,

    requestStarted: action((method: string, url: string) => {
        apiState.requests++;
    }),
    requestSucceeded: action((method: string, url: string) => {
        apiState.requests--;
    }),
    requestFailed: action((method: string, url: string) => {
        apiState.requests--;
    }),
});

/**
 * Common code for accessing web services.
 */
export default class BaseAPI<ItemType = any> {
    url: string;
    config: any;

    constructor(baseUrl: string, config) {
        this.url = baseUrl;
        this.config = config || {};
    }

    list(args?): Promise<ItemType[]> {
        return this.request('GET', this.url, args);
    }

    get(id: PrimaryKey): Promise<ItemType> {
        return this.request('GET', this.url + id + '/');
    }

    /**
     * Make a HTTP request.
     * @param method HTTP method to use, if applicable
     * @param url URL to send the request to
     * @param query Optional query params
     * @param payload Optional payload
     * @returns Async response
     */
    protected request<T = any>(method: string, url: string, query?, payload?): Promise<T> {
        if (process.env.NODE_ENV === 'test') {
            console.trace('Unmocked API request:', method, url);
            return Promise.reject();
        }

        const fetchImpl = this.config.fetch || fetch;

        // Run this outside the request context to avoid MobX invariant violations.
        setTimeout(() => {
            apiState.requestStarted(method, url);
        }, 0);

        return fetchImpl(this.encodeQuery(url, query), {
            method,
            body: this.encodePayload(payload),
            credentials: 'include',
            headers: {
                // Sending this in a request with no payload isn't strictly wrong.
                'content-type': 'application/json',
                // This better be up to date, no way to update it right now.
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
        }).then(res => this.handleResponse(res)
        ).catch(err => this.handleError(err)
        ).then((success) => {
            apiState.requestSucceeded(method, url);
            return success;
        }, (error) => {
            apiState.requestFailed(method, url);
            throw error;
        });
    }

    /**
     * Encode query part into the URL.
     * Note that there's no standard for how to encode non-trivial data.
     * @param url URL part
     * @param [query] Query "payload"
     * @returns URL, with encoded payload if possible
     */
    protected encodeQuery(url: string, query?) {
        if (!query) {
            return url;
        }
        return `${url}?${qs.stringify(query)}`;
    }

    /**
     * Encode payload object for the request body.
     * Leaves out any keys starting with an underscore ('_').
     * @param [payload] Payload to encode
     * @returns Encoded payload, if any.
     */
    protected encodePayload(payload) {
        if (payload) {
            return JSON.stringify(
                payload,
                (key, val) => {
                    // prefix for implementation details in other logic
                    if (key[0] !== '_') {
                        return val;
                    }
                },
            );
        }
    }

    /**
     * Handle a HTTP/Fetch response. Note that fetch does not auto-reject
     * on error-like status code, so we do it here.
     * @param {Response} response
     */
    protected handleResponse(response: Response) {
        if (response.status === 401) {
            globalState.sessionExpired();
        }
        if (!response.ok) {
            throw response;
        }
        const { status } = response;
        if (status === 204 || status === 205) {
            // This is probably less accident-prone than returning null
            return {
                _status: status,
            };
        }
        // there might be some interesting payload, try to decode it
        return response.json().then((payload) => {
            // all payloads should be objects anyway to block eval() fail
            if (payload && typeof payload === 'object') {
                payload._status = status;
            }
            // freeze the object; we don't want to mutate it directly anywhere
            // (this also speeds up Vue and possibly MobX a lot)
            return Object.freeze(payload);
        }, (error) => {
            // tslint:disable-next-line no-console
            console.warn('Unable to decode payload:', error);
            throw error;
        });
    }

    /**
     * Handle any error that may have occurred.
     * @param error
     */
    protected handleError(errorResponse: Response | any) {
        // see if we got any kind of payload
        if (typeof errorResponse.json !== 'function') {
            throw errorResponse;
        }
        return errorResponse.json().then((payload) => {
            throw Object.freeze(payload);
        }, (error) => {
            // tslint:disable-next-line no-console
            console.warn('unable to decode error payload:', error);
            throw error;
        });
    }
}
