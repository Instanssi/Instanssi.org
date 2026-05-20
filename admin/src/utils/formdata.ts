import { getFile, type FileValue } from "./file";

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
