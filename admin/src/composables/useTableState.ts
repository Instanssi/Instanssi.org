import { debounce } from "lodash-es";
import { type ComputedRef, type Ref, type WritableComputedRef, computed, ref, watch } from "vue";
import { type LocationQuery, useRoute, useRouter } from "vue-router";

import type { LoadArgs } from "@/services/utils/query_tools";

type SortItem = { key: string; order: "asc" | "desc" };
type BooleanFilter = WritableComputedRef<boolean | null>;

export type SortOrder = "asc" | "desc";

export interface TableStateOptions {
    /** Default items per page */
    defaultPerPage?: number;
    /** Available page size options */
    pageSizeOptions?: number[];
    /** Custom filter keys to sync with URL (e.g., ['compo', 'status']) */
    filterKeys?: string[];
    /** Debounce delay for URL updates (ms) */
    urlUpdateDelay?: number;
    /** Default sort when no sort is specified in URL */
    defaultSort?: {
        key: string;
        order: SortOrder;
    };
}

export interface TableState {
    page: Ref<number>;
    perPage: Ref<number>;
    search: Ref<string>;
    sortBy: Ref<string | null>;
    sortOrder: Ref<SortOrder>;
    /** Sort state in Vuetify v-data-table format - pass to :sort-by prop */
    sortByArray: ComputedRef<SortItem[]>;
    filters: Ref<Record<string, string | null>>;
    pageSizeOptions: number[];
    /** Call this when table options change */
    onOptionsUpdate: (args: LoadArgs) => void;
    /** Get a filter value as number or null */
    getFilterAsNumber: (key: string) => number | null;
    /** Set a filter value */
    setFilter: (key: string, value: string | number | null) => void;
    /** Reset pagination to page 1 (useful when filters change) */
    resetPage: () => void;
    /** Create a writable computed ref for a boolean filter (true/false/null) */
    useBooleanFilter: (key: string) => BooleanFilter;
}

/**
 * Composable that syncs table pagination/filter state with URL query parameters.
 * This allows the table state to persist across navigation.
 */
export function useTableState(options: TableStateOptions = {}): TableState {
    const {
        defaultPerPage = 25,
        pageSizeOptions = [25, 50, 100],
        filterKeys = [],
        urlUpdateDelay = 100,
        defaultSort,
    } = options;

    const route = useRoute();
    const router = useRouter();

    // State refs
    const page = ref(1);
    const perPage = ref(defaultPerPage);
    const search = ref("");
    const sortBy: Ref<string | null> = ref(null);
    const sortOrder: Ref<SortOrder> = ref("asc");
    const filters: Ref<Record<string, string | null>> = ref({});

    // Initialize filters object with null values
    for (const key of filterKeys) {
        filters.value[key] = null;
    }

    /**
     * Parse URL query parameters and update state
     */
    function readFromUrl(): void {
        const query = route.query;

        // Page
        if (query.page && typeof query.page === "string") {
            const parsed = parseInt(query.page, 10);
            if (!isNaN(parsed) && parsed > 0) {
                page.value = parsed;
            }
        } else {
            page.value = 1;
        }

        // Items per page
        if (query.perPage && typeof query.perPage === "string") {
            const parsed = parseInt(query.perPage, 10);
            if (!isNaN(parsed) && pageSizeOptions.includes(parsed)) {
                perPage.value = parsed;
            }
        } else {
            perPage.value = defaultPerPage;
        }

        // Search
        if (query.search && typeof query.search === "string") {
            search.value = query.search;
        } else {
            search.value = "";
        }

        // Sort
        if (query.sortBy && typeof query.sortBy === "string") {
            sortBy.value = query.sortBy;
        } else if (defaultSort) {
            sortBy.value = defaultSort.key;
        } else {
            sortBy.value = null;
        }
        if (query.sortOrder && typeof query.sortOrder === "string") {
            if (query.sortOrder === "asc" || query.sortOrder === "desc") {
                sortOrder.value = query.sortOrder;
            }
        } else if (defaultSort) {
            sortOrder.value = defaultSort.order;
        } else {
            sortOrder.value = "asc";
        }

        // Custom filters
        for (const key of filterKeys) {
            if (query[key] && typeof query[key] === "string") {
                filters.value[key] = query[key];
            } else {
                filters.value[key] = null;
            }
        }
    }

    // Read initial state from URL immediately (before template renders)
    readFromUrl();

    /**
     * Build query object from current state
     */
    function buildQuery(): LocationQuery {
        const query: LocationQuery = {};

        // Only include non-default values to keep URL clean
        if (page.value !== 1) {
            query.page = String(page.value);
        }
        if (perPage.value !== defaultPerPage) {
            query.perPage = String(perPage.value);
        }
        if (search.value) {
            query.search = search.value;
        }
        if (sortBy.value) {
            query.sortBy = sortBy.value;
            if (sortOrder.value !== "asc") {
                query.sortOrder = sortOrder.value;
            }
        }

        // Custom filters
        for (const key of filterKeys) {
            if (filters.value[key] !== null && filters.value[key] !== "") {
                query[key] = filters.value[key]!;
            }
        }

        return query;
    }

    /**
     * Update URL with current state (debounced)
     */
    const updateUrl = debounce(() => {
        const query = buildQuery();
        // Use replace to avoid cluttering history with every keystroke
        router.replace({ query });
    }, urlUpdateDelay);

    /**
     * Handle table options update from v-data-table-server
     */
    function onOptionsUpdate(args: LoadArgs): void {
        page.value = args.page;
        perPage.value = args.itemsPerPage;
        search.value = args.search;

        if (args.sortBy.length > 0) {
            sortBy.value = args.sortBy[0]!.key;
            sortOrder.value = args.sortBy[0]!.order;
        } else if (defaultSort) {
            sortBy.value = defaultSort.key;
            sortOrder.value = defaultSort.order;
        } else {
            sortBy.value = null;
            sortOrder.value = "asc";
        }

        updateUrl();
    }

    /**
     * Get a filter value as a number, or null if not set/invalid
     */
    function getFilterAsNumber(key: string): number | null {
        const value = filters.value[key];
        if (value === null || value === undefined || value === "") return null;
        const parsed = parseInt(value, 10);
        return isNaN(parsed) ? null : parsed;
    }

    /**
     * Set a filter value and update URL
     */
    function setFilter(key: string, value: string | number | null): void {
        if (value === null || value === "") {
            filters.value[key] = null;
        } else {
            filters.value[key] = String(value);
        }
        updateUrl();
    }

    /**
     * Reset to page 1 (useful when filters change)
     */
    function resetPage(): void {
        page.value = 1;
        updateUrl();
    }

    /**
     * Create a writable computed ref for a boolean filter.
     * Converts between boolean | null in the UI and string | null in the URL.
     */
    function useBooleanFilter(key: string): BooleanFilter {
        return computed({
            get: () => {
                const value = filters.value[key];
                return value === "true" ? true : value === "false" ? false : null;
            },
            set: (value: boolean | null) => {
                setFilter(key, value === null ? null : String(value));
                resetPage();
            },
        });
    }

    /**
     * Sort state in Vuetify v-data-table format
     */
    const sortByArray = computed<SortItem[]>(() => {
        if (sortBy.value) {
            return [{ key: sortBy.value, order: sortOrder.value }];
        }
        return [];
    });

    // Watch for browser back/forward navigation
    watch(
        () => route.query,
        () => {
            readFromUrl();
        }
    );

    // Watch filters and update URL
    watch(
        filters,
        () => {
            updateUrl();
        },
        { deep: true }
    );

    return {
        page,
        perPage,
        search,
        sortBy,
        sortOrder,
        sortByArray,
        filters,
        pageSizeOptions,
        onOptionsUpdate,
        getFilterAsNumber,
        setFilter,
        resetPage,
        useBooleanFilter,
    };
}
