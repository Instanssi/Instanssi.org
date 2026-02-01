import { describe, expect, it } from "vitest";

import { prepareFileField, toFormData } from "./formdata";

describe("toFormData", () => {
    describe("with null and undefined values", () => {
        it("should send empty string for null values", () => {
            const result = toFormData({ name: "test", empty: null });
            expect(result.get("name")).toBe("test");
            expect(result.get("empty")).toBe("");
        });

        it("should skip undefined values", () => {
            const result = toFormData({ name: "test", empty: undefined });
            expect(result.get("name")).toBe("test");
            expect(result.has("empty")).toBe(false);
        });

        it("should distinguish null from undefined", () => {
            const result = toFormData({ a: null, b: undefined });
            const entries = Array.from(result.entries());
            expect(entries).toHaveLength(1);
            expect(result.get("a")).toBe("");
            expect(result.has("b")).toBe(false);
        });
    });

    describe("with File values", () => {
        it("should append File directly", () => {
            const file = new File(["content"], "test.txt", { type: "text/plain" });
            const result = toFormData({ document: file });

            const formFile = result.get("document");
            expect(formFile).toBeInstanceOf(File);
            expect((formFile as File).name).toBe("test.txt");
        });

        it("should preserve file content type", () => {
            const file = new File(["image"], "photo.jpg", { type: "image/jpeg" });
            const result = toFormData({ image: file });

            const formFile = result.get("image") as File;
            expect(formFile.type).toBe("image/jpeg");
        });

        it("should handle File array (v-file-input with multiple)", () => {
            const file1 = new File(["content1"], "file1.txt", { type: "text/plain" });
            const file2 = new File(["content2"], "file2.txt", { type: "text/plain" });
            const result = toFormData({ document: [file1, file2] });

            // Should only use the first file
            const formFile = result.get("document");
            expect(formFile).toBeInstanceOf(File);
            expect((formFile as File).name).toBe("file1.txt");
        });

        it("should skip empty File array", () => {
            const result = toFormData({ document: [] as File[] });
            expect(result.has("document")).toBe(false);
        });
    });

    describe("with boolean values", () => {
        it("should convert true to 'true' string", () => {
            const result = toFormData({ active: true });
            expect(result.get("active")).toBe("true");
        });

        it("should convert false to 'false' string", () => {
            const result = toFormData({ active: false });
            expect(result.get("active")).toBe("false");
        });
    });

    describe("with number values", () => {
        it("should convert integers to strings", () => {
            const result = toFormData({ count: 42 });
            expect(result.get("count")).toBe("42");
        });

        it("should convert floats to strings", () => {
            const result = toFormData({ price: 19.99 });
            expect(result.get("price")).toBe("19.99");
        });

        it("should convert zero to string", () => {
            const result = toFormData({ value: 0 });
            expect(result.get("value")).toBe("0");
        });

        it("should convert negative numbers to strings", () => {
            const result = toFormData({ offset: -10 });
            expect(result.get("offset")).toBe("-10");
        });
    });

    describe("with string values", () => {
        it("should preserve string values", () => {
            const result = toFormData({ name: "Test Name" });
            expect(result.get("name")).toBe("Test Name");
        });

        it("should handle empty strings", () => {
            const result = toFormData({ description: "" });
            expect(result.get("description")).toBe("");
        });

        it("should handle strings with special characters", () => {
            const result = toFormData({ text: "Hello\nWorld\t!" });
            expect(result.get("text")).toBe("Hello\nWorld\t!");
        });
    });

    describe("with mixed object", () => {
        it("should handle mixed types correctly", () => {
            const file = new File([""], "doc.pdf");
            const result = toFormData({
                name: "Product",
                price: 29.99,
                active: true,
                hidden: false,
                description: null,
                optional: undefined,
                document: file,
            });

            expect(result.get("name")).toBe("Product");
            expect(result.get("price")).toBe("29.99");
            expect(result.get("active")).toBe("true");
            expect(result.get("hidden")).toBe("false");
            expect(result.get("description")).toBe(""); // null becomes empty string
            expect(result.has("optional")).toBe(false); // undefined is skipped
            expect(result.get("document")).toBeInstanceOf(File);
        });

        it("should include all non-undefined entries", () => {
            const result = toFormData({
                a: "string",
                b: 123,
                c: true,
                d: null,
                e: undefined,
                f: false,
            });

            const keys = Array.from(result.keys());
            expect(keys).toHaveLength(5); // e (undefined) is skipped
            expect(result.get("a")).toBe("string");
            expect(result.get("b")).toBe("123");
            expect(result.get("c")).toBe("true");
            expect(result.get("d")).toBe("");
            expect(result.has("e")).toBe(false);
            expect(result.get("f")).toBe("false");
        });
    });
});

describe("prepareFileField", () => {
    it("should return File when given a File", () => {
        const file = new File(["content"], "test.txt");
        const result = prepareFileField(file);
        expect(result).toBe(file);
    });

    it("should return first File when given File array", () => {
        const file1 = new File(["content1"], "file1.txt");
        const file2 = new File(["content2"], "file2.txt");
        const result = prepareFileField([file1, file2]);
        expect(result).toBe(file1);
    });

    it("should return null when given null (to clear the file)", () => {
        const result = prepareFileField(null);
        expect(result).toBeNull();
    });

    it("should return undefined when given undefined", () => {
        const result = prepareFileField(undefined);
        expect(result).toBeUndefined();
    });

    it("should return undefined when given empty array", () => {
        const result = prepareFileField([]);
        expect(result).toBeUndefined();
    });
});
