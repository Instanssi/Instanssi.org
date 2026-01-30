import { describe, it, expect } from "vitest";
import { toLocalDatetime, toISODatetime, ADMIN_TIMEZONE } from "./datetime";

describe("datetime utilities", () => {
    describe("ADMIN_TIMEZONE", () => {
        it("should be Europe/Helsinki", () => {
            expect(ADMIN_TIMEZONE).toBe("Europe/Helsinki");
        });
    });

    describe("toLocalDatetime", () => {
        it("returns empty string for null input", () => {
            expect(toLocalDatetime(null)).toBe("");
        });

        it("returns empty string for undefined input", () => {
            expect(toLocalDatetime(undefined)).toBe("");
        });

        it("returns empty string for empty string input", () => {
            expect(toLocalDatetime("")).toBe("");
        });

        it("converts UTC to Helsinki winter time (EET, UTC+2)", () => {
            // January 15, 2024 12:00:00 UTC -> 14:00 in Helsinki (EET)
            const result = toLocalDatetime("2024-01-15T12:00:00Z");
            expect(result).toBe("2024-01-15T14:00");
        });

        it("converts UTC to Helsinki summer time (EEST, UTC+3)", () => {
            // July 15, 2024 12:00:00 UTC -> 15:00 in Helsinki (EEST)
            const result = toLocalDatetime("2024-07-15T12:00:00Z");
            expect(result).toBe("2024-07-15T15:00");
        });

        it("handles DST transition: winter to summer", () => {
            // March 31, 2024 00:59:59 UTC -> 02:59 EET (just before DST change)
            const beforeDST = toLocalDatetime("2024-03-31T00:59:59Z");
            expect(beforeDST).toBe("2024-03-31T02:59");

            // March 31, 2024 01:00:00 UTC -> 04:00 EEST (just after DST change)
            const afterDST = toLocalDatetime("2024-03-31T01:00:00Z");
            expect(afterDST).toBe("2024-03-31T04:00");
        });

        it("handles DST transition: summer to winter", () => {
            // October 27, 2024 00:59:59 UTC -> 03:59 EEST (just before DST change)
            const beforeDST = toLocalDatetime("2024-10-27T00:59:59Z");
            expect(beforeDST).toBe("2024-10-27T03:59");

            // October 27, 2024 01:00:00 UTC -> 03:00 EET (just after DST change)
            const afterDST = toLocalDatetime("2024-10-27T01:00:00Z");
            expect(afterDST).toBe("2024-10-27T03:00");
        });

        it("handles midnight crossing", () => {
            // UTC midnight should become 02:00 or 03:00 in Helsinki
            const winterMidnight = toLocalDatetime("2024-01-15T00:00:00Z");
            expect(winterMidnight).toBe("2024-01-15T02:00");

            const summerMidnight = toLocalDatetime("2024-07-15T00:00:00Z");
            expect(summerMidnight).toBe("2024-07-15T03:00");
        });

        it("handles ISO string with timezone offset", () => {
            // Input with +00:00 offset
            const result = toLocalDatetime("2024-01-15T12:00:00+00:00");
            expect(result).toBe("2024-01-15T14:00");
        });

        it("handles ISO string with non-UTC offset", () => {
            // 12:00 at UTC+5 is 07:00 UTC, which is 09:00 in Helsinki (winter)
            const result = toLocalDatetime("2024-01-15T12:00:00+05:00");
            expect(result).toBe("2024-01-15T09:00");
        });
    });

    describe("toISODatetime", () => {
        it("returns null for empty string", () => {
            expect(toISODatetime("")).toBeNull();
        });

        it("converts Helsinki winter time to UTC", () => {
            // 14:00 in Helsinki (EET) -> 12:00 UTC
            const result = toISODatetime("2024-01-15T14:00");
            expect(result).toBe("2024-01-15T12:00:00Z");
        });

        it("converts Helsinki summer time to UTC", () => {
            // 15:00 in Helsinki (EEST) -> 12:00 UTC
            const result = toISODatetime("2024-07-15T15:00");
            expect(result).toBe("2024-07-15T12:00:00Z");
        });

        it("handles midnight in Helsinki", () => {
            // Midnight in Helsinki winter -> 22:00 previous day UTC
            const winter = toISODatetime("2024-01-15T00:00");
            expect(winter).toBe("2024-01-14T22:00:00Z");

            // Midnight in Helsinki summer -> 21:00 previous day UTC
            const summer = toISODatetime("2024-07-15T00:00");
            expect(summer).toBe("2024-07-14T21:00:00Z");
        });

        it("handles end of day in Helsinki", () => {
            // 23:59 in Helsinki winter -> 21:59 UTC
            const winter = toISODatetime("2024-01-15T23:59");
            expect(winter).toBe("2024-01-15T21:59:00Z");

            // 23:59 in Helsinki summer -> 20:59 UTC
            const summer = toISODatetime("2024-07-15T23:59");
            expect(summer).toBe("2024-07-15T20:59:00Z");
        });

        it("handles DST transition dates", () => {
            // March 31, 2024 - DST starts at 03:00 (clocks jump to 04:00)
            // 02:00 is still EET (UTC+2)
            const beforeDST = toISODatetime("2024-03-31T02:00");
            expect(beforeDST).toBe("2024-03-31T00:00:00Z");

            // 04:00 is EEST (UTC+3)
            const afterDST = toISODatetime("2024-03-31T04:00");
            expect(afterDST).toBe("2024-03-31T01:00:00Z");
        });
    });

    describe("round-trip conversion", () => {
        it("preserves winter time through round-trip", () => {
            const original = "2024-01-15T14:30";
            const iso = toISODatetime(original);
            const backToLocal = toLocalDatetime(iso);
            expect(backToLocal).toBe(original);
        });

        it("preserves summer time through round-trip", () => {
            const original = "2024-07-15T14:30";
            const iso = toISODatetime(original);
            const backToLocal = toLocalDatetime(iso);
            expect(backToLocal).toBe(original);
        });

        it("preserves midnight through round-trip", () => {
            const original = "2024-01-15T00:00";
            const iso = toISODatetime(original);
            const backToLocal = toLocalDatetime(iso);
            expect(backToLocal).toBe(original);
        });

        it("preserves end of day through round-trip", () => {
            const original = "2024-07-15T23:59";
            const iso = toISODatetime(original);
            const backToLocal = toLocalDatetime(iso);
            expect(backToLocal).toBe(original);
        });

        it("preserves date near DST transition through round-trip", () => {
            // Just before DST starts
            const beforeDST = "2024-03-31T02:30";
            expect(toLocalDatetime(toISODatetime(beforeDST))).toBe(beforeDST);

            // Just after DST starts
            const afterDST = "2024-03-31T04:30";
            expect(toLocalDatetime(toISODatetime(afterDST))).toBe(afterDST);
        });
    });
});
