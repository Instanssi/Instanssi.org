/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BlogEntry } from "./BlogEntry";
export type PaginatedBlogEntryList = {
    count: number;
    next?: string | null;
    previous?: string | null;
    results: Array<BlogEntry>;
};
