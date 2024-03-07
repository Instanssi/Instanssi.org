import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { faDashboard, faRightFromBracket } from "@fortawesome/free-solid-svg-icons";
import type { App } from "vue";

library.add(faDashboard, faRightFromBracket);

export function setupIcons(app: App) {
    app.component("font-awesome-icon", FontAwesomeIcon);
}
