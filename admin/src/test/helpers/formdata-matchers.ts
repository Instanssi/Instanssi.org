import { expect } from "vitest";

/**
 * Convert FormData to a plain object for easier assertions.
 * Note: Files are converted to their name string.
 *
 * @param formData - FormData to convert
 * @returns Plain object with string values
 */
export function formDataToObject(formData: FormData): Record<string, string | File> {
    const result: Record<string, string | File> = {};
    formData.forEach((value, key) => {
        if (value instanceof File) {
            result[key] = value;
        } else {
            result[key] = value;
        }
    });
    return result;
}

/**
 * Assert that FormData contains expected key-value pairs.
 *
 * @param formData - FormData to check
 * @param expected - Expected key-value pairs
 */
export function expectFormDataContains(
    formData: FormData,
    expected: Record<string, string | File>
): void {
    const actual = formDataToObject(formData);

    for (const [key, value] of Object.entries(expected)) {
        if (value instanceof File) {
            expect(actual[key]).toBeInstanceOf(File);
            expect((actual[key] as File).name).toBe(value.name);
        } else {
            expect(actual[key]).toBe(value);
        }
    }
}

/**
 * Assert that FormData contains a specific key with any value.
 *
 * @param formData - FormData to check
 * @param key - Key to check for
 */
export function expectFormDataHasKey(formData: FormData, key: string): void {
    expect(formData.has(key)).toBe(true);
}

/**
 * Assert that FormData does not contain a specific key.
 *
 * @param formData - FormData to check
 * @param key - Key that should not be present
 */
export function expectFormDataNotHasKey(formData: FormData, key: string): void {
    expect(formData.has(key)).toBe(false);
}

/**
 * Assert that FormData contains a File value for a specific key.
 *
 * @param formData - FormData to check
 * @param key - Key to check
 * @param expectedName - Optional: expected file name
 */
export function expectFormDataHasFile(
    formData: FormData,
    key: string,
    expectedName?: string
): void {
    const value = formData.get(key);
    expect(value).toBeInstanceOf(File);
    if (expectedName) {
        expect((value as File).name).toBe(expectedName);
    }
}
