import BaseAPI from './BaseAPI';
import Cookies from 'cookies-js';
import {
    ICompetition,
    ICompetitionParticipation,
    ICompo,
    ICompoEntry,
    IEvent,
    IProgrammeEvent,
    IUser,
    IVoteCodeRequest,
    IVoteCode,
    IUserVote,
} from 'src/api/interfaces';

import config from 'src/config';

/**
 * The Instanssi REST service, abstracted for convenience (and not fetch()'ing from components).
 */
export default class InstanssiREST {
    currentUser: SessionAPI;
    events: EventsAPI;
    compos: ComposAPI;
    competitions: CompetitionsAPI;
    programme: ProgrammeAPI;
    compoEntries: CompoEntriesAPI;
    competitionParticipations: CompetitionParticipationsAPI;
    songs: SongsAPI;
    userCompoEntries: UserCompoEntriesAPI;
    userCompetitionParticipations: UserCompetitionParticipationsAPI;
    voteCodes: UserVoteCodesAPI;
    voteCodeRequests: UserVoteCodeRequestsAPI;
    userVotes: UserVotesAPI;

    constructor(baseUrl: string, config = {}) {
        this.currentUser = new SessionAPI(baseUrl, config);
        this.events = new EventsAPI(baseUrl, config);
        this.compos = new ComposAPI(baseUrl, config);
        this.competitions = new CompetitionsAPI(baseUrl, config);
        this.programme = new ProgrammeAPI(baseUrl, config);
        this.compoEntries = new CompoEntriesAPI(baseUrl, config);
        this.competitionParticipations = new CompetitionParticipationsAPI(baseUrl, config);
        this.userCompoEntries = new UserCompoEntriesAPI(baseUrl, config);
        this.userCompetitionParticipations = new UserCompetitionParticipationsAPI(baseUrl, config);
        this.songs = new SongsAPI(baseUrl, config);
        this.voteCodes = new UserVoteCodesAPI(baseUrl, config);
        this.voteCodeRequests = new UserVoteCodeRequestsAPI(baseUrl, config);
        this.userVotes = new UserVotesAPI(baseUrl, config);
    }
}

/**
 * API for getting the user's current session.
 * Not really a full REST resource, but whatever.
 */
class SessionAPI extends BaseAPI<IUser> {
    constructor(baseUrl, config) {
        super(baseUrl + '/current_user/', config);
    }

    /**
     * Get the current user logged into the rest of the site.
     * Rejects if there is no user.
     */
    get(): Promise<IUser> {
        return this.request('GET', this.url);
    }
}

class EventsAPI extends BaseAPI<IEvent> {
    constructor(baseUrl, config) {
        super(baseUrl + '/events/', config);
    }
}

class ComposAPI extends BaseAPI<ICompo> {
    constructor(baseUrl, config) {
        super(baseUrl + '/compos/', config);
    }
}

class CompetitionsAPI extends BaseAPI<ICompetition> {
    constructor(baseUrl, config) {
        super(baseUrl + '/competitions/', config);
    }
}

class ProgrammeAPI extends BaseAPI<IProgrammeEvent> {
    constructor(baseUrl, config) {
        super(baseUrl + '/programme_events/', config);
    }
}

class CompoEntriesAPI extends BaseAPI<ICompoEntry> {
    constructor(baseUrl, config) {
        super(baseUrl + '/compo_entries/', config);
    }
}

/**
 * API for managing the user's own compo entries.
 *
 * Requires an authenticated user.
 */
class UserCompoEntriesAPI extends BaseAPI<ICompoEntry> {
    constructor(baseUrl, config) {
        super(baseUrl + '/user_entries/', config);
    }

    /**
     * Create a new compo entry.
     *
     * Entries must have an entry file, and possibly an image file.
     * Source files are not required.
     */
    create(request) {
        const { sourcefile, imagefile_original, ...rest } = request;
        const fetchImpl = (this.config.fetch as typeof fetch) || fetch;

        const formData = new FormData();

        // This had better be up to date, no way to refresh it right now.
        formData.append('csrfmiddlewaretoken', Cookies.get('csrftoken'));

        // Append basic inputs into the form data.
        Object.keys(rest).forEach(key => {
            formData.append(key, rest[key]);
        });

        // The BE doesn't like receiving a null value for these, so leave them out
        // unless they're actually set.
        if (sourcefile) {
            formData.append('sourcefile', sourcefile);
        }
        if (imagefile_original) {
            formData.append('imagefile_original', imagefile_original);
        }

        return fetchImpl(this.url, {
            method: 'POST',
            body: formData,
            credentials: 'include',
        }).then((response) => this.handleResponse(response))
        .catch((error) => this.handleError(error));
    }

    update(id, request): Promise<any> {
        const { entryfile, sourcefile, imagefile_original, ...rest } = request;
        const fetchImpl = (this.config.fetch as typeof fetch) || fetch;

        const formData = new FormData();

        // formData.append('csrfmiddlewaretoken', Cookies.get('csrftoken'));

        // Append basic inputs into the form data.
        Object.keys(rest).forEach(key => {
            formData.append(key, rest[key]);
        });

        const handleFile = (name, value) => {
            // Not passing a file leaves it as-is, which is what "undefined" means here.
            // Null files are to be deleted.
            // New files will replace existing ones.
            // FIXME: The API doesn't seem to accept null/empty file. Check specs.
            if (typeof value !== 'undefined') {
                formData.append(name, value === null ? '' : value);
            }
        };

        handleFile('entryfile', entryfile);
        handleFile('sourcefile', sourcefile);
        handleFile('imagefile_original', imagefile_original);

        // Yes, Django requires the trailing slash.
        return fetchImpl(`${this.url}${id}/`, {
            method: 'PATCH',
            body: formData,
            credentials: 'include',
            headers: {
                // This better be up to date.
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
        }).then((response) => this.handleResponse(response))
        .catch((error) => this.handleError(error));
    }
}

class CompetitionParticipationsAPI extends BaseAPI<ICompetitionParticipation> {
    constructor(baseUrl, config) {
        super(baseUrl + '/competition_participations/', config);
    }
}

/**
 * API for managing the user's own competition participations.
 *
 * Requires an authenticated user.
 */
class UserCompetitionParticipationsAPI extends BaseAPI<ICompetitionParticipation> {
    constructor(baseUrl, config) {
        super(baseUrl + '/user_participations/', config);
    }

    create(request) {
        return this.request('POST', this.url, null, request);
    }
}

class SongsAPI extends BaseAPI {
    constructor(baseUrl, config) {
        super(baseUrl + '/songs/', config);
    }
}

class UserVoteCodesAPI extends BaseAPI<IVoteCode> {
    constructor(baseUrl, config) {
        super(baseUrl + '/user_vote_codes/', config);
    }

    create(request) {
        return this.request('POST', this.url, null, request);
    }
}

class UserVoteCodeRequestsAPI extends BaseAPI<IVoteCodeRequest> {
    constructor(baseUrl, config) {
        super(baseUrl + '/user_vote_code_requests/', config);
    }

    create(request) {
        return this.request('POST', this.url, null, request);
    }
}

class UserVotesAPI extends BaseAPI<IUserVote> {
    constructor(baseUrl, config) {
        super(baseUrl + '/user_votes/', config);
    }

    getVotes(compo: number) {
        return this.request<IUserVote[]>('GET', this.url, { compo });
    }

    /**
     * Post some votes for a compo. The "entries" is a list of entry ids in preferred order.
     */
    setVotes(request: { compo: number, entries: number[] }) {
        return this.request('POST', this.url, null, request);
    }
}

export const api = new InstanssiREST(config.API_URL);
