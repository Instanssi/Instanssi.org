import { getFile, type FileValue } from "./file";

/**
 * Serialize a single value to FormData.
 * Based on @hey-api/openapi-ts serializeFormDataPair.
 */
function serializeFormDataPair(data: FormData, key: string, value: unknown): void {
    if (typeof value === "string" || value instanceof Blob) {
        data.append(key, value);
    } else if (value instanceof Date) {
        data.append(key, value.toISOString());
    } else {
        data.append(key, JSON.stringify(value));
    }
}

/**
 * Convert an object to FormData for multipart/form-data uploads.
 *
 * Based on @hey-api/openapi-ts formDataBodySerializer, but with one difference:
 * - null values are sent as empty string (to clear the field)
 * - undefined values are skipped (not sent)
 */
export function toFormData(obj: Record<string, unknown>): FormData {
    const data = new FormData();

    for (const [key, value] of Object.entries(obj)) {
        if (value === undefined) {
            continue;
        }
        if (value === null) {
            data.append(key, "");
            continue;
        }
        if (Array.isArray(value)) {
            value.forEach((v) => serializeFormDataPair(data, key, v));
        } else {
            serializeFormDataPair(data, key, value);
        }
    }

    return data;
}

/**
 * Prepare a file field value for FormData serialization.
 *
 * This function handles the three-state logic for file fields:
 * - undefined (not touched) -> returns undefined (field will be skipped in FormData)
 * - null (explicitly cleared) -> returns null (field will be sent as empty string to clear it)
 * - File (new file selected) -> returns the File
 *
 * @param value - The value from the file field
 * @returns File if a new file was selected, null if cleared, undefined if not touched
 */
export function prepareFileField(value: FileValue | undefined): File | null | undefined {
    // Not touched - don't send the field
    if (value === undefined) {
        return undefined;
    }
    // Explicitly cleared - send empty string to clear
    if (value === null) {
        return null;
    }
    // New file selected
    return getFile(value);
}
