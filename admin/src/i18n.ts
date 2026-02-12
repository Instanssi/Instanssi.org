import { createI18n } from "vue-i18n";

import enLocale from "@/locales/en.json";
import fiLocale from "@/locales/fi.json";

type DateTimeFormatOptions = Record<string, Intl.DateTimeFormatOptions>;

export const SUPPORTED_LOCALES = ["en", "fi"] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];
const DEFAULT_LOCALE = "en";

/** Human-readable names for each supported locale. */
export const LOCALE_NAMES: Record<SupportedLocale, string> = {
    en: "English",
    fi: "Suomi",
};
const ADMIN_TIMEZONE = "Europe/Helsinki";

/** Pick the best supported locale from the browser's language preferences. */
function detectLocale(): string {
    const candidates = navigator.languages?.length ? navigator.languages : [navigator.language];
    for (const lang of candidates) {
        if (!lang) continue;
        const primary = (lang.split("-")[0] ?? lang).toLowerCase();
        if ((SUPPORTED_LOCALES as readonly string[]).includes(primary)) {
            return primary;
        }
    }
    return DEFAULT_LOCALE;
}

/** Check if a string is a supported locale. */
export function isSupportedLocale(value: string): value is SupportedLocale {
    return (SUPPORTED_LOCALES as readonly string[]).includes(value);
}

/** Set the active locale. */
export function setLocale(locale: SupportedLocale): void {
    i18n.global.locale.value = locale;
}

// Add timezone to datetime formats so Vue I18n's d() function displays times in Helsinki
const baseDatetimeFormats = enLocale["datetimeFormats"] as DateTimeFormatOptions;
const datetimeFormatsWithTimezone: DateTimeFormatOptions = {
    short: {
        ...baseDatetimeFormats.short,
        timeZone: ADMIN_TIMEZONE,
    },
    long: {
        ...baseDatetimeFormats.long,
        timeZone: ADMIN_TIMEZONE,
    },
};

export const i18n = createI18n({
    legacy: false,
    locale: detectLocale(),
    fallbackLocale: DEFAULT_LOCALE,
    messages: {
        en: enLocale["translations"],
        fi: fiLocale["translations"],
    },
    datetimeFormats: {
        en: datetimeFormatsWithTimezone,
        fi: datetimeFormatsWithTimezone,
    },
});
