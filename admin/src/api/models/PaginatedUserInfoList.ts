/* generated using openapi-typescript-codegen -- do not edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { UserInfo } from "./UserInfo";

export type PaginatedUserInfoList = {
    count: number;
    next?: string | null;
    previous?: string | null;
    results: Array<UserInfo>;
};
