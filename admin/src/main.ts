import "@/assets/main.scss";
import "@vueup/vue-quill/dist/vue-quill.snow.css";
import "vue-toastification/dist/index.css";

// Libs
import { createApp } from "vue";
import { createVuetify } from "vuetify";
import { createI18n } from "vue-i18n";
import { aliases, fa } from "vuetify/iconsets/fa-svg";
import toast, { type PluginOptions } from "vue-toastification";

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
    const toastOptions: PluginOptions = {
        maxToasts: 2,
    };

    setupIcons(app);
    app.use(router);
    app.use(vuetify);
    app.use(i18n);
    app.use(toast, toastOptions);
    app.mount("#app");
}

// Check it we are logged in first, and only then initialize the application.
// This way we can already make decisions in the router about which page to show.
useAuth().refreshStatus().then(init);
