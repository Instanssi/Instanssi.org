/**
 * Convert ISO datetime string to datetime-local input format.
 * Handles timezone offset to display in local time.
 */
export function toLocalDatetime(isoString: string | null | undefined): string {
    if (!isoString) return "";
    const date = new Date(isoString);
    const offset = date.getTimezoneOffset();
    const localDate = new Date(date.getTime() - offset * 60 * 1000);
    return localDate.toISOString().slice(0, 16);
}

/**
 * Convert datetime-local input value to ISO format.
 * Returns null for empty strings.
 */
export function toISODatetime(localString: string): string | null {
    if (!localString) return null;
    const date = new Date(localString);
    return date.toISOString();
}
