import { Temporal } from "temporal-polyfill";

export const ADMIN_TIMEZONE = "Europe/Helsinki";

/**
 * Convert ISO datetime string to datetime-local input format.
 * Always uses Europe/Helsinki timezone regardless of browser timezone.
 */
export function toLocalDatetime(isoString: string | null | undefined): string {
    if (!isoString) return "";
    const instant = Temporal.Instant.from(isoString);
    const helsinkiDateTime = instant.toZonedDateTimeISO(ADMIN_TIMEZONE);
    // PlainDateTime.toString() gives YYYY-MM-DDTHH:MM:SS format
    // Slice to 16 chars for datetime-local input (YYYY-MM-DDTHH:MM)
    return helsinkiDateTime.toPlainDateTime().toString().slice(0, 16);
}

/**
 * Convert datetime-local input value to ISO format.
 * Interprets input as Europe/Helsinki time and converts to UTC.
 * Returns null for empty strings.
 */
export function toISODatetime(localString: string): string | null {
    if (!localString) return null;
    const plainDateTime = Temporal.PlainDateTime.from(localString);
    const helsinkiZoned = plainDateTime.toZonedDateTime(ADMIN_TIMEZONE);
    return helsinkiZoned.toInstant().toString();
}
