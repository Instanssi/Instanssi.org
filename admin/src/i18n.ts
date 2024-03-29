import { createI18n } from "vue-i18n";
import enLocale from "@/locales/en.json";

export const i18n = createI18n({
    legacy: false,
    locale: "en",
    fallbackLocale: "en",
    messages: {
        en: enLocale["translations"],
    },
    datetimeFormats: {
        // @ts-ignore
        en: enLocale["datetimeFormats"],
    },
});
