import { library } from "@fortawesome/fontawesome-svg-core";
import {
    // Our own icons
    faGithub,
    faGoogle,
    faSteam,
} from "@fortawesome/free-brands-svg-icons";
import {
    // for vuetify
    faCircle as farCircle,
    faDotCircle as farDotCircle,
    faSquare as farSquare,
    faStar as farStar,
} from "@fortawesome/free-regular-svg-icons";
import {
    // Our own icons
    faBlog,
    faCalendarDays,
    faDashboard,
    faFloppyDisk,
    faLock,
    faPenToSquare,
    faRightFromBracket,
    faRightToBracket,
    faSitemap,
    faXmark,
    faStrikethrough,
    faBold,
    faItalic,
    faUnderline,
} from "@fortawesome/free-solid-svg-icons";
import {
    // For vuetify
    faArrowDown,
    faArrowUp,
    faArrowsAltV,
    faBars,
    faCalendar,
    faCaretDown,
    faCheck,
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
    // These are our own imports
    library.add(
        faDashboard,
        faRightFromBracket,
        faRightToBracket,
        faBlog,
        faSitemap,
        faLock,
        faXmark,
        faFloppyDisk,
        faPenToSquare,
        faCalendarDays,
        faStrikethrough,
        faBold,
        faItalic,
        faUnderline,
    );
    library.add(faGoogle, faSteam, faGithub);

    // These are used by vuetify and imported for the standard set
    library.add(
        faChevronUp,
        faCheck,
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
    app.component("font-awesome-icon", FontAwesomeIcon);
}
