import { beforeEach, describe, expect, it, vi } from "vitest";
import { useTableState } from "./useTableState";
import type { LoadArgs } from "@/services/utils/query_tools";

// Mock route query - will be modified by tests
let mockQuery: Record<string, string> = {};
const mockReplace = vi.fn();

vi.mock("vue-router", () => ({
    useRouter: () => ({
        replace: mockReplace,
    }),
    useRoute: () => ({
        query: mockQuery,
    }),
}));

// Mock lodash debounce to execute immediately
vi.mock("lodash-es", async () => {
    const actual = await vi.importActual("lodash-es");
    return {
        ...actual,
        debounce: (fn: (...args: unknown[]) => unknown) => fn,
    };
});

// Helper to create LoadArgs with proper typing
function createLoadArgs(overrides: Partial<Omit<LoadArgs, "groupBy">> = {}): LoadArgs {
    return {
        page: 1,
        itemsPerPage: 25,
        search: "",
        sortBy: [],
        groupBy: undefined as never,
        ...overrides,
    };
}

describe("useTableState", () => {
    beforeEach(() => {
        mockQuery = {};
        mockReplace.mockClear();
    });

    describe("default state", () => {
        it("initializes with default values when URL has no params", () => {
            const state = useTableState();

            expect(state.page.value).toBe(1);
            expect(state.perPage.value).toBe(25);
            expect(state.search.value).toBe("");
            expect(state.sortBy.value).toBeNull();
            expect(state.sortOrder.value).toBe("asc");
            expect(state.pageSizeOptions).toEqual([25, 50, 100]);
        });

        it("uses custom default options", () => {
            const state = useTableState({
                defaultPerPage: 50,
                pageSizeOptions: [10, 50, 200],
            });

            expect(state.perPage.value).toBe(50);
            expect(state.pageSizeOptions).toEqual([10, 50, 200]);
        });

        it("initializes filter keys with null values", () => {
            const state = useTableState({
                filterKeys: ["status", "category"],
            });

            expect(state.filters.value).toEqual({
                status: null,
                category: null,
            });
        });
    });

    describe("reading from URL", () => {
        it("reads page from URL", () => {
            mockQuery = { page: "3" };
            const state = useTableState();

            expect(state.page.value).toBe(3);
        });

        it("ignores invalid page values", () => {
            mockQuery = { page: "invalid" };
            const state = useTableState();

            expect(state.page.value).toBe(1);
        });

        it("ignores negative page values", () => {
            mockQuery = { page: "-1" };
            const state = useTableState();

            expect(state.page.value).toBe(1);
        });

        it("reads perPage from URL when it matches options", () => {
            mockQuery = { perPage: "50" };
            const state = useTableState();

            expect(state.perPage.value).toBe(50);
        });

        it("ignores perPage when not in options", () => {
            mockQuery = { perPage: "99" };
            const state = useTableState();

            expect(state.perPage.value).toBe(25);
        });

        it("reads search from URL", () => {
            mockQuery = { search: "test query" };
            const state = useTableState();

            expect(state.search.value).toBe("test query");
        });

        it("reads sortBy from URL", () => {
            mockQuery = { sortBy: "name" };
            const state = useTableState();

            expect(state.sortBy.value).toBe("name");
        });

        it("reads sortOrder from URL", () => {
            mockQuery = { sortBy: "name", sortOrder: "desc" };
            const state = useTableState();

            expect(state.sortOrder.value).toBe("desc");
        });

        it("ignores invalid sortOrder values", () => {
            mockQuery = { sortBy: "name", sortOrder: "invalid" };
            const state = useTableState();

            expect(state.sortOrder.value).toBe("asc");
        });

        it("defaults sortOrder to asc when sortBy is in URL but sortOrder is not", () => {
            mockQuery = { sortBy: "name" };
            const state = useTableState({
                initialSort: { key: "id", order: "desc" },
            });

            expect(state.sortBy.value).toBe("name");
            expect(state.sortOrder.value).toBe("asc");
        });

        it("reads custom filter values from URL", () => {
            mockQuery = { status: "active", category: "5" };
            const state = useTableState({
                filterKeys: ["status", "category"],
            });

            expect(state.filters.value.status).toBe("active");
            expect(state.filters.value.category).toBe("5");
        });
    });

    describe("sortByArray computed", () => {
        it("returns empty array when no sort is set", () => {
            const state = useTableState();

            expect(state.sortByArray.value).toEqual([]);
        });

        it("returns sort item when sortBy is set", () => {
            mockQuery = { sortBy: "name", sortOrder: "desc" };
            const state = useTableState();

            expect(state.sortByArray.value).toEqual([{ key: "name", order: "desc" }]);
        });
    });

    describe("onOptionsUpdate", () => {
        it("updates state from table options", () => {
            const state = useTableState();

            state.onOptionsUpdate(
                createLoadArgs({
                    page: 2,
                    itemsPerPage: 50,
                    search: "test",
                    sortBy: [{ key: "name", order: "desc" }],
                })
            );

            expect(state.page.value).toBe(2);
            expect(state.perPage.value).toBe(50);
            expect(state.search.value).toBe("test");
            expect(state.sortBy.value).toBe("name");
            expect(state.sortOrder.value).toBe("desc");
        });

        it("clears sort when sortBy array is empty", () => {
            mockQuery = { sortBy: "name", sortOrder: "desc" };
            const state = useTableState();

            state.onOptionsUpdate(createLoadArgs());

            expect(state.sortBy.value).toBeNull();
            expect(state.sortOrder.value).toBe("asc");
        });

        it("updates URL after state change", () => {
            const state = useTableState();

            state.onOptionsUpdate(
                createLoadArgs({
                    page: 2,
                    itemsPerPage: 50,
                    search: "test",
                    sortBy: [{ key: "name", order: "desc" }],
                })
            );

            expect(mockReplace).toHaveBeenCalledWith({
                query: {
                    page: "2",
                    perPage: "50",
                    search: "test",
                    sortBy: "name",
                    sortOrder: "desc",
                },
            });
        });
    });

    describe("setFilter", () => {
        it("sets filter value as string", () => {
            const state = useTableState({ filterKeys: ["status"] });

            state.setFilter("status", "active");

            expect(state.filters.value.status).toBe("active");
        });

        it("converts number to string", () => {
            const state = useTableState({ filterKeys: ["category"] });

            state.setFilter("category", 5);

            expect(state.filters.value.category).toBe("5");
        });

        it("sets null for null value", () => {
            const state = useTableState({ filterKeys: ["status"] });
            state.filters.value.status = "active";

            state.setFilter("status", null);

            expect(state.filters.value.status).toBeNull();
        });

        it("sets null for empty string", () => {
            const state = useTableState({ filterKeys: ["status"] });
            state.filters.value.status = "active";

            state.setFilter("status", "");

            expect(state.filters.value.status).toBeNull();
        });

        it("updates URL after setting filter", () => {
            const state = useTableState({ filterKeys: ["status"] });

            state.setFilter("status", "active");

            expect(mockReplace).toHaveBeenCalledWith({
                query: { status: "active" },
            });
        });
    });

    describe("getFilterAsNumber", () => {
        it("returns number for valid numeric string", () => {
            const state = useTableState({ filterKeys: ["category"] });
            state.filters.value.category = "42";

            expect(state.getFilterAsNumber("category")).toBe(42);
        });

        it("returns null for null filter value", () => {
            const state = useTableState({ filterKeys: ["category"] });

            expect(state.getFilterAsNumber("category")).toBeNull();
        });

        it("returns null for empty string", () => {
            const state = useTableState({ filterKeys: ["category"] });
            state.filters.value.category = "";

            expect(state.getFilterAsNumber("category")).toBeNull();
        });

        it("returns null for non-numeric string", () => {
            const state = useTableState({ filterKeys: ["category"] });
            state.filters.value.category = "invalid";

            expect(state.getFilterAsNumber("category")).toBeNull();
        });

        it("returns null for undefined filter key", () => {
            const state = useTableState({ filterKeys: [] });

            expect(state.getFilterAsNumber("nonexistent")).toBeNull();
        });
    });

    describe("resetPage", () => {
        it("resets page to 1", () => {
            const state = useTableState();
            state.page.value = 5;

            state.resetPage();

            expect(state.page.value).toBe(1);
        });

        it("updates URL after reset", () => {
            const state = useTableState();
            state.page.value = 5;

            state.resetPage();

            // Page 1 is default, so it should not appear in query
            expect(mockReplace).toHaveBeenCalledWith({ query: {} });
        });
    });

    describe("useBooleanFilter", () => {
        it("returns null when filter is not set", () => {
            const state = useTableState({ filterKeys: ["active"] });
            const filter = state.useBooleanFilter("active");

            expect(filter.value).toBeNull();
        });

        it("returns true when filter is 'true'", () => {
            mockQuery = { active: "true" };
            const state = useTableState({ filterKeys: ["active"] });
            const filter = state.useBooleanFilter("active");

            expect(filter.value).toBe(true);
        });

        it("returns false when filter is 'false'", () => {
            mockQuery = { active: "false" };
            const state = useTableState({ filterKeys: ["active"] });
            const filter = state.useBooleanFilter("active");

            expect(filter.value).toBe(false);
        });

        it("returns null for other string values", () => {
            const state = useTableState({ filterKeys: ["active"] });
            state.filters.value.active = "invalid";
            const filter = state.useBooleanFilter("active");

            expect(filter.value).toBeNull();
        });

        it("sets filter to 'true' when assigned true", () => {
            const state = useTableState({ filterKeys: ["active"] });
            const filter = state.useBooleanFilter("active");

            filter.value = true;

            expect(state.filters.value.active).toBe("true");
        });

        it("sets filter to 'false' when assigned false", () => {
            const state = useTableState({ filterKeys: ["active"] });
            const filter = state.useBooleanFilter("active");

            filter.value = false;

            expect(state.filters.value.active).toBe("false");
        });

        it("sets filter to null when assigned null", () => {
            const state = useTableState({ filterKeys: ["active"] });
            state.filters.value.active = "true";
            const filter = state.useBooleanFilter("active");

            filter.value = null;

            expect(state.filters.value.active).toBeNull();
        });

        it("resets page when filter changes", () => {
            const state = useTableState({ filterKeys: ["active"] });
            state.page.value = 5;
            const filter = state.useBooleanFilter("active");

            filter.value = true;

            expect(state.page.value).toBe(1);
        });

        it("updates URL when filter changes", () => {
            const state = useTableState({ filterKeys: ["active"] });
            const filter = state.useBooleanFilter("active");

            filter.value = true;

            expect(mockReplace).toHaveBeenCalledWith({
                query: { active: "true" },
            });
        });
    });

    describe("URL query building", () => {
        it("omits default values from URL", () => {
            const state = useTableState();

            state.onOptionsUpdate(createLoadArgs());

            expect(mockReplace).toHaveBeenCalledWith({ query: {} });
        });

        it("omits sortOrder when it is 'asc' (default)", () => {
            const state = useTableState();

            state.onOptionsUpdate(
                createLoadArgs({
                    sortBy: [{ key: "name", order: "asc" }],
                })
            );

            expect(mockReplace).toHaveBeenCalledWith({
                query: { sortBy: "name" },
            });
        });

        it("includes sortOrder when it is 'desc'", () => {
            const state = useTableState();

            state.onOptionsUpdate(
                createLoadArgs({
                    sortBy: [{ key: "name", order: "desc" }],
                })
            );

            expect(mockReplace).toHaveBeenCalledWith({
                query: { sortBy: "name", sortOrder: "desc" },
            });
        });

        it("includes custom filters in URL", () => {
            const state = useTableState({ filterKeys: ["status", "type"] });

            state.setFilter("status", "active");
            state.setFilter("type", "ticket");

            // Last call should include both filters
            const lastCall = mockReplace.mock.calls[mockReplace.mock.calls.length - 1];
            expect(lastCall).toBeDefined();
            expect(lastCall![0].query).toEqual({
                status: "active",
                type: "ticket",
            });
        });

        it("excludes null filter values from URL", () => {
            const state = useTableState({ filterKeys: ["status"] });

            state.setFilter("status", null);

            expect(mockReplace).toHaveBeenCalledWith({ query: {} });
        });
    });
});
