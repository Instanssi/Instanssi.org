/**
 * Convert an object to FormData for multipart/form-data uploads.
 * Handles File objects, booleans, and primitive values.
 */
export function toFormData(obj: Record<string, unknown>): FormData {
    const formData = new FormData();
    for (const [key, value] of Object.entries(obj)) {
        if (value === undefined || value === null) continue;
        if (value instanceof File) {
            formData.append(key, value);
        } else if (typeof value === "boolean") {
            formData.append(key, value ? "true" : "false");
        } else {
            formData.append(key, String(value));
        }
    }
    return formData;
}
