import { createApp } from "vue";
import toast, { type PluginOptions } from "vue-toastification";
import { createVuetify } from "vuetify";
import { aliases, fa } from "vuetify/iconsets/fa-svg";

import App from "@/App.vue";
import "@/assets/main.scss";
import { i18n } from "@/i18n";
import { setupIcons } from "@/icons";
import router from "@/router";
import { setupClient } from "@/client";
import { useAuth } from "@/services/auth";
import { vuetifyTipTap } from "@/tiptap";

function init() {
    const app = createApp(App);
    const vuetify = createVuetify({
        icons: {
            defaultSet: "fa",
            aliases,
            sets: { fa },
        },
    });
    const toastOptions: PluginOptions = {
        maxToasts: 5,
    };

    setupIcons(app);
    app.use(router);
    app.use(vuetify);
    app.use(vuetifyTipTap);
    app.use(i18n);
    app.use(toast, toastOptions);
    app.mount("#app");
}

// Check it we are logged in first, and only then initialize the application.
// This way we can already make decisions in the router about which page to show.
setupClient();
useAuth().refreshStatus().then(init);
