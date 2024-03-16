import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import type { App } from "vue";

// These are our own imports
import {
    faDashboard,
    faRightFromBracket,
    faRightToBracket,
    faBlog,
    faSitemap,
    faLock,
    faFloppyDisk,
    faXmark,
    faPenToSquare,
} from "@fortawesome/free-solid-svg-icons";

// These are used by vuetify and imported for the standard set
import {
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
    faEyeDropper,
} from "@fortawesome/free-solid-svg-icons";
import {
    faSquare as farSquare,
    faDotCircle as farDotCircle,
    faCircle as farCircle,
    faStar as farStar,
} from "@fortawesome/free-regular-svg-icons";
import { faGoogle, faSteam, faGithub } from "@fortawesome/free-brands-svg-icons";

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
        faPenToSquare
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
