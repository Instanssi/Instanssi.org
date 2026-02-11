import { createI18n } from "vue-i18n";

import enLocale from "@/locales/en.json";
import fiLocale from "@/locales/fi.json";

type DateTimeFormatOptions = Record<string, Intl.DateTimeFormatOptions>;

const ADMIN_TIMEZONE = "Europe/Helsinki";

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
    locale: "en",
    fallbackLocale: "en",
    messages: {
        en: enLocale["translations"],
        fi: fiLocale["translations"],
    },
    datetimeFormats: {
        en: datetimeFormatsWithTimezone,
        fi: datetimeFormatsWithTimezone,
    },
});
