import { describe, it, expect } from 'vitest'
import { getLoadArgs } from "@/services/utils/query_tools";


describe('getLoadArgs', () => {
    it('works with full input', () => {
        const out = getLoadArgs({
            page: 5,
            itemsPerPage: 10,
            sortBy: [
                {
                    key: "test",
                    order: "desc",
                }
            ],
            groupBy: undefined,
            search: "search",
        });
        expect(out).toStrictEqual({
            limit: 10,
            offset: 40,
            ordering: "-test",
            search: "search",
        });
    });
});
