import { createI18n } from "vue-i18n";

import enLocale from "@/locales/en.json";

type DateTimeFormatOptions = Record<string, Intl.DateTimeFormatOptions>;

export const i18n = createI18n({
    legacy: false,
    locale: "en",
    fallbackLocale: "en",
    messages: {
        en: enLocale["translations"],
    },
    datetimeFormats: {
        en: enLocale["datetimeFormats"] as DateTimeFormatOptions,
    },
});
