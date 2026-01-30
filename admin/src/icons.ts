/**
 * FontAwesome icon library setup for Vuetify integration.
 *
 * This file registers icons in the FontAwesome library for use with Vuetify's
 * string-based icon system (e.g., prepend-icon="fas fa-check").
 *
 * PREFERRED APPROACH: When using icons in your own components, prefer importing
 * icons directly and using the FontAwesomeIcon component:
 *
 *   import { faCheck } from "@fortawesome/free-solid-svg-icons";
 *   import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
 *
 *   <FontAwesomeIcon :icon="faCheck" />
 *
 * This approach provides better tree-shaking and type safety.
 * Only add icons to this file if they're needed by Vuetify components.
 */
import { library } from "@fortawesome/fontawesome-svg-core";
import {
    // For Vuetify
    faCircle as farCircle,
    faDotCircle as farDotCircle,
    faSquare as farSquare,
    faStar as farStar,
} from "@fortawesome/free-regular-svg-icons";
import {
    // For Vuetify
    faArrowDown,
    faArrowUp,
    faArrowsAltV,
    faBars,
    faCalendar,
    faCaretDown,
    faCheckCircle,
    faCheckSquare,
    faChevronDown,
    faChevronLeft,
    faChevronRight,
    faChevronUp,
    faCircle,
    faEdit,
    faExclamation,
    faExclamationTriangle,
    faEyeDropper,
    faInfoCircle,
    faMinus,
    faMinusSquare,
    faPaperclip,
    faPlus,
    faStar,
    faStarHalf,
    faStepBackward,
    faStepForward,
    faSync,
    faTimes,
    faTimesCircle,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import type { App } from "vue";

export function setupIcons(app: App): void {
    // Icons used by Vuetify components
    library.add(
        faChevronUp,
        faTimesCircle,
        faTimes,
        faCheckCircle,
        faInfoCircle,
        faExclamation,
        faExclamationTriangle,
        faChevronLeft,
        faChevronRight,
        faChevronDown,
        faCheckSquare,
        faMinusSquare,
        faCircle,
        faArrowUp,
        faArrowDown,
        faBars,
        faCaretDown,
        faEdit,
        faStar,
        faStarHalf,
        faSync,
        faStepBackward,
        faStepForward,
        faArrowsAltV,
        faPaperclip,
        faPlus,
        faMinus,
        faCalendar,
        faEyeDropper
    );
    library.add(farSquare, farDotCircle, farCircle, farStar);

    // This is required by v-icon and other components
    app.component("FontAwesomeIcon", FontAwesomeIcon);
}
