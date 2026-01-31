import { describe, expect, it } from "vitest";

import { getLoadArgs, getSortString, type LoadArgs } from "./query_tools";

describe("getLoadArgs", () => {
    describe("offset calculation", () => {
        it("should calculate offset 0 for page 1", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [],
                groupBy: undefined as never,
                search: "",
            };
            expect(getLoadArgs(args).offset).toBe(0);
        });

        it("should calculate correct offset for page 2", () => {
            const args: LoadArgs = {
                page: 2,
                itemsPerPage: 10,
                sortBy: [],
                groupBy: undefined as never,
                search: "",
            };
            expect(getLoadArgs(args).offset).toBe(10);
        });

        it("should calculate correct offset for page 5 with 25 items per page", () => {
            const args: LoadArgs = {
                page: 5,
                itemsPerPage: 25,
                sortBy: [],
                groupBy: undefined as never,
                search: "",
            };
            expect(getLoadArgs(args).offset).toBe(100);
        });
    });

    describe("limit", () => {
        it("should pass itemsPerPage as limit", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 50,
                sortBy: [],
                groupBy: undefined as never,
                search: "",
            };
            expect(getLoadArgs(args).limit).toBe(50);
        });
    });

    describe("search passthrough", () => {
        it("should pass empty search string", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [],
                groupBy: undefined as never,
                search: "",
            };
            expect(getLoadArgs(args).search).toBe("");
        });

        it("should pass search term unchanged", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [],
                groupBy: undefined as never,
                search: "test query",
            };
            expect(getLoadArgs(args).search).toBe("test query");
        });
    });

    describe("ordering", () => {
        it("should pass undefined ordering when no sort", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [],
                groupBy: undefined as never,
                search: "",
            };
            expect(getLoadArgs(args).ordering).toBeUndefined();
        });

        it("should pass correct ordering for ascending sort", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [{ key: "name", order: "asc" }],
                groupBy: undefined as never,
                search: "",
            };
            expect(getLoadArgs(args).ordering).toBe("name");
        });

        it("should pass correct ordering for descending sort", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [{ key: "created", order: "desc" }],
                groupBy: undefined as never,
                search: "",
            };
            expect(getLoadArgs(args).ordering).toBe("-created");
        });
    });
});

describe("getSortString", () => {
    describe("empty sortBy", () => {
        it("should return undefined for empty sortBy array", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [],
                groupBy: undefined as never,
                search: "",
            };
            expect(getSortString(args)).toBeUndefined();
        });
    });

    describe("ascending sort", () => {
        it("should return key without prefix for ascending", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [{ key: "username", order: "asc" }],
                groupBy: undefined as never,
                search: "",
            };
            expect(getSortString(args)).toBe("username");
        });

        it("should handle snake_case keys", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [{ key: "created_at", order: "asc" }],
                groupBy: undefined as never,
                search: "",
            };
            expect(getSortString(args)).toBe("created_at");
        });
    });

    describe("descending sort", () => {
        it("should return key with minus prefix for descending", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [{ key: "price", order: "desc" }],
                groupBy: undefined as never,
                search: "",
            };
            expect(getSortString(args)).toBe("-price");
        });

        it("should handle snake_case keys with desc", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [{ key: "updated_at", order: "desc" }],
                groupBy: undefined as never,
                search: "",
            };
            expect(getSortString(args)).toBe("-updated_at");
        });
    });

    describe("multiple sort entries", () => {
        it("should only use first sortBy entry", () => {
            const args: LoadArgs = {
                page: 1,
                itemsPerPage: 10,
                sortBy: [
                    { key: "first", order: "asc" },
                    { key: "second", order: "desc" },
                ],
                groupBy: undefined as never,
                search: "",
            };
            expect(getSortString(args)).toBe("first");
        });
    });
});
