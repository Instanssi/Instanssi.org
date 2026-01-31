/**
 * File type for v-file-input validation - can return File, File[], or null
 */
export type FileValue = File | File[] | null;

/**
 * Helper to get a single File from v-file-input value.
 * v-file-input can return File, File[], or null depending on the `multiple` prop.
 *
 * @param value - The value from v-file-input
 * @returns The first File if available, undefined otherwise
 */
export function getFile(value: FileValue | undefined): File | undefined {
    if (!value) return undefined;
    if (Array.isArray(value)) return value[0];
    return value;
}
