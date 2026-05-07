import _get from 'lodash/get';
import _template from 'lodash/template';
import _orderBy from 'lodash/orderBy';
import { runInAction, computed, reaction, action } from 'mobx';
import { observable } from 'mobx';
import moment from 'moment';

import config from 'src/config';
import i18n from '../i18n';
import { api } from '../api';
import { LazyStore } from 'src/stores';
import EventInfo from './EventInfo';
import { toast } from 'react-toastify';
import { L } from 'src/common';


export interface INotificationMessage {
    id: number;
    text: string;
    type?: string;
    values?: {};
}

/**
 * Application-wide state.
 */
class GlobalState {
    userStore = new LazyStore(() => api.currentUser.get());

    /** Default party time zone. */
    partyTimeZone = 'Europe/Helsinki';

    /**
     * Override default browser timezone behavior by setting this
     * to a moment-timezone tz id. Null leaves the formatting as-is
     * and shows device-local time.
     *
     * This should only matter where times are displayed.
     */
    @observable tzOverride: string | null = this.partyTimeZone;

    /** Current user, if known. Don't even try to mutate. */
    get user() {
        return this.userStore.value;
    }
    /**
     * Current language code (ISO 639 style).
     * @todo Save language in local storage for now.
     */
    @observable.ref language = config.DEFAULT_LOCALE;
    /** Current translation object. Translating text looks for keys in this. */
    @observable.ref translation: any = { };
    /** Current time in milliseconds, updating once per second. */
    @observable.ref timeSec = new Date().valueOf();
    /** Current time in milliseconds, updating once per minute. */
    @observable.ref timeMin = new Date().valueOf();
    /** Messages the user should probably see. */
    @observable.shallow messages: INotificationMessage[] = [];
    nextMessageId = 0;

    /** Several things could use a list of party events, so it's available here. */
    events = new LazyStore(async () => {
        const events = await api.events.list();
        const sorted = _orderBy(events, event => event.date, 'desc');
        return sorted.map(eventObject => new EventInfo(this.api, eventObject));
    });

    /** The site API made available here for convenience. */
    api = api;

    constructor() {
        // FIXME: Try to persist the state and bring it back on reload?
        setInterval(() => {
            this.timeSec = new Date().valueOf();
        }, 1000);
        setInterval(() => {
            this.timeMin = new Date().valueOf();
        }, 60000);

        this.loadPersistentState();
        // Should be only one global state, so it's ok if we don't have a way to drop this.
        reaction(
            () => this.persistentState,
            (state) => {
                this.savePersistentState(state);
            },
        );
        this.setLanguage(this.languageCode);
        this.continueSession();
    }

    /**
     * Construct a Moment object that behaves according to the party's time zone when
     * formatting to text, querying start/end of day and so on.
     * @param value Input to construct timestamp from.
     */
    getMoment(value: number | string | moment.Moment | Date) {
        if (this.tzOverride) {
            return moment(value).tz(this.tzOverride);
        }
        return moment(value);
    }

    get persistentState() {
        return {
            language: this.language,
        };
    }

    savePersistentState(state) {
        try {
            localStorage.setItem('kompomaatti', JSON.stringify(state));
        } catch (error) {
            console.warn('Failed to save state: ' + error);
        }
    }

    loadPersistentState() {
        try {
            const stored = localStorage.getItem('kompomaatti');
            if (stored) {
                const state = JSON.parse(stored);
                this.language = state.language || config.DEFAULT_LOCALE;
            }
        } catch (error) {
            console.warn('Failed to load state: ' + error);
        }
    }

    /**
     * Most relevant-looking event of the current events list.
     */
    @computed
    get currentEvent() {
        const events = this.events.value;
        if (!events) {
            return null;
        }
        // The events are in descending order by date.
        return events[0];
    }

    get momentLocale() {
        // TODO: Are language codes always the same as moment locales?
        return this.language;
    }

    get languageCode() {
        return this.language;
    }

    /**
     * The one and only way to get translated text.
     * @param name Translation name, e.g. 'user.firstName'
     * @param values Optional arguments for translation (spec pending)
     * @returns Translated text string
     */
    translate = (name: string, values?: {[key: string]: string}) => {
        const text = _get(this.translation, name, name) as string;
        // TODO: Spec pluralisation, etc.
        if (values) {
            return _template(text)(values);
        }
        return text;
    }

    /**
     * Check for existing session, assign user, fetch translations before continuing.
     * @returns User profile after session check
     */
    async continueSession() {
        return this.userStore.refresh();
    }

    /**
     * Clear the current user's info and maybe notify them about this.
     */
    sessionExpired() {
        if (this.user) {
            this.userStore.clear();

            // FIXME yay, dependency loop
            // toast.info(L.getText('session.expired'));
            this.postMessage('danger', 'session.expired');
        }
    }

    @action
    postMessage(type: string, text: string, values?: {}) {
        this.messages.push({
            id: this.nextMessageId++,
            type,
            text,
            values,
        });
        setTimeout(action(() => {
            this.messages.splice(0, 1);
        }), 5000);
    }

    /**
     * Change the UI language. May require fetching a new translation file.
     * @param languageCode Language code like 'fi-FI'.
     * @returns Promise that resolves when the language switch finishes.
     */
    setLanguage(code: string) {
        const lang = i18n[code];

        if (!lang) {
            throw new Error('No translation found: ' + code);
        }

        return lang.fetch().then(
            (translation) => runInAction(() => {
                this.language = code;
                this.translation = translation;
            }),
            (error) => {
                console.warn('Unable to load translation:', code, error);
                throw error;
            },
        );
    }
}

const globalState = new GlobalState();
export default globalState;

if (process.env.NODE_ENV === 'development') {
    // sneaky devmode trick
    (window as any)._globalState = globalState;
}
