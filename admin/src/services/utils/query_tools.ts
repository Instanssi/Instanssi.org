export type LoadArgs = {
    page: number;
    itemsPerPage: number;
    sortBy: [
        {
            key: string;
            order: "asc" | "desc";
        },
    ];
    groupBy: any;
    search: string;
};

export function getLoadArgs(args: LoadArgs) {
    return {
        offset: (args.page - 1) * args.itemsPerPage,
        limit: args.itemsPerPage,
        sortBy: getSortString(args),
    };
}

export function getSortString(args: LoadArgs) {
    if (args.sortBy.length <= 0) {
        return undefined;
    }
    const sortBy = args.sortBy[0];
    if (sortBy.order === "asc") {
        return `${sortBy.key}`;
    } else {
        return `-${sortBy.key}`;
    }
}
