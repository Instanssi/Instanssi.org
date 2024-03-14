import "@/assets/main.scss";
import "@vueup/vue-quill/dist/vue-quill.snow.css";

// Libs
import { createApp } from "vue";
import { createVuetify } from "vuetify";
import { createI18n } from "vue-i18n";
import { aliases, fa } from "vuetify/iconsets/fa-svg";

// Our own stuff
import App from "@/App.vue";
import router from "@/router";
import { setupIcons } from "@/icons";
import { useAuth } from "@/services/auth";
import enLocale from "@/locales/en.json";

function init() {
    const app = createApp(App);
    const vuetify = createVuetify({
        icons: {
            defaultSet: "fa",
            aliases,
            sets: { fa },
        },
    });
    const i18n = createI18n({
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

    setupIcons(app);
    app.use(router);
    app.use(vuetify);
    app.use(i18n);
    app.mount("#app");
}

useAuth().refreshStatus().then(init);
