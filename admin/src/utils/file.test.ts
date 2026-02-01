import { describe, expect, it } from "vitest";

import { getFile, type FileValue } from "./file";

describe("getFile", () => {
    describe("with null or undefined", () => {
        it("should return undefined for null", () => {
            expect(getFile(null)).toBeUndefined();
        });

        it("should return undefined for undefined", () => {
            expect(getFile(undefined)).toBeUndefined();
        });
    });

    describe("with File", () => {
        it("should return the File when given a single File", () => {
            const file = new File(["content"], "test.txt", { type: "text/plain" });
            expect(getFile(file)).toBe(file);
        });

        it("should preserve the file name", () => {
            const file = new File(["content"], "document.pdf", { type: "application/pdf" });
            const result = getFile(file);
            expect(result?.name).toBe("document.pdf");
        });

        it("should preserve the file type", () => {
            const file = new File(["image data"], "photo.png", { type: "image/png" });
            const result = getFile(file);
            expect(result?.type).toBe("image/png");
        });
    });

    describe("with File[]", () => {
        it("should return the first File from an array", () => {
            const file1 = new File(["content1"], "first.txt");
            const file2 = new File(["content2"], "second.txt");
            expect(getFile([file1, file2])).toBe(file1);
        });

        it("should return undefined for empty array", () => {
            expect(getFile([])).toBeUndefined();
        });

        it("should return the only file from single-element array", () => {
            const file = new File(["content"], "only.txt");
            expect(getFile([file])).toBe(file);
        });
    });

    describe("type safety", () => {
        it("should handle FileValue type correctly", () => {
            const values: FileValue[] = [
                null,
                new File([""], "test.txt"),
                [new File([""], "arr.txt")],
            ];

            const results = values.map(getFile);
            expect(results[0]).toBeUndefined();
            expect(results[1]).toBeInstanceOf(File);
            expect(results[2]).toBeInstanceOf(File);
        });
    });
});
