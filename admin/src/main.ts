import "@/assets/main.scss";

// Libs
import { createApp } from "vue";
import { createVuetify } from "vuetify";
import { aliases, fa } from "vuetify/iconsets/fa-svg";

// Our own stuff
import App from "@/App.vue";
import router from "@/router";
import { setupIcons } from "@/icons";
import { useAuth } from "@/services/auth";

function init() {
    const app = createApp(App);
    const vuetify = createVuetify({
        icons: {
            defaultSet: "fa",
            aliases,
            sets: { fa },
        },
    });

    setupIcons(app);
    app.use(router);
    app.use(vuetify);
    app.mount("#app");
}

useAuth().refreshStatus().then(init);
