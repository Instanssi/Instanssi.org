type SortArgs = {
    key: string;
    order: "asc" | "desc";
};

// These should match Vuetify data-table args
export type LoadArgs = {
    page: number;
    itemsPerPage: number;
    sortBy: SortArgs[];
    groupBy: any;
    search: string;
};

// These are passed to the API client
export type ApiArgs = {
    offset: number;
    limit: number;
    sortBy: string | undefined;
};

/**
 * Converts vuetify arguments to API compatible form
 */
export function getLoadArgs(args: LoadArgs): ApiArgs {
    return {
        offset: (args.page - 1) * args.itemsPerPage,
        limit: args.itemsPerPage,
        sortBy: getSortString(args),
    };
}

/**
 * Convert sort arguments from vuetify to API compatible form.
 */
export function getSortString(args: LoadArgs): string | undefined {
    if (args.sortBy.length <= 0) {
        return undefined;
    }
    const sortBy: SortArgs = args.sortBy[0];
    if (sortBy.order === "asc") {
        return `${sortBy.key}`;
    } else {
        return `-${sortBy.key}`;
    }
}
