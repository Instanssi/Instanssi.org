import { describe, expect, it } from "vitest";

import { hasMultipleAuthors } from "./diploma";

describe("diploma utilities", () => {
    describe("hasMultipleAuthors", () => {
        it("returns false for single author", () => {
            expect(hasMultipleAuthors("John Doe")).toBe(false);
        });

        it("returns true for authors separated by /", () => {
            expect(hasMultipleAuthors("John / Jane")).toBe(true);
            expect(hasMultipleAuthors("Alpha/Beta/Gamma")).toBe(true);
        });

        it("returns true for authors separated by comma", () => {
            expect(hasMultipleAuthors("John, Jane")).toBe(true);
            expect(hasMultipleAuthors("Alpha,Beta,Gamma")).toBe(true);
        });

        it('returns true for authors separated by " ja "', () => {
            expect(hasMultipleAuthors("John ja Jane")).toBe(true);
            expect(hasMultipleAuthors("Alpha ja Beta ja Gamma")).toBe(true);
        });

        it('returns true for authors separated by " & "', () => {
            expect(hasMultipleAuthors("John & Jane")).toBe(true);
            expect(hasMultipleAuthors("Alpha & Beta & Gamma")).toBe(true);
        });

        it("handles mixed separators", () => {
            expect(hasMultipleAuthors("John, Jane & Bob")).toBe(true);
        });

        it("does not falsely detect partial matches", () => {
            // "janne" contains "ja" but not " ja "
            expect(hasMultipleAuthors("Janne")).toBe(false);
            // "rajamäki" contains "ja" but not " ja "
            expect(hasMultipleAuthors("Rajamäki")).toBe(false);
        });
    });
});
