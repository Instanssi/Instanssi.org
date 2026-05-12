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
 * Based on @hey-api/openapi-ts formDataBodySerializer, but:
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
