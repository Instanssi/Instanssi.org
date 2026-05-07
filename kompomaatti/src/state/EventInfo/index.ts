import { observable, computed } from 'mobx';
import moment from 'moment';

import InstanssiREST from 'src/api';
import {
    IEvent,
    IProgrammeEvent,
    ICompo,
    ICompetition,
    ICompoEntry,
} from 'src/api/interfaces';
import { LazyStore } from 'src/stores';

const storeOptions = {
    // Accommodate changes in the structure of space and time
    // by auto-refreshing previously fetched stores after a few minutes.
    // (this only triggers when something new tries to access them)
    refreshInterval: 1000 * 60 * 2,
};

/**
 * Collects data related to a specific event under one object for easy access and caching.
 */
export default class EventInfo {
    @observable.ref event: IEvent;

    compos = new LazyStore(
        () => this.api.compos.list(this.query), storeOptions);
    competitions = new LazyStore(
        () => this.api.competitions.list(this.query), storeOptions);
    programme = new LazyStore(
        () => this.api.programme.list(this.query), storeOptions);
    myEntries = new LazyStore(
        () => this.api.userCompoEntries.list(this.query), storeOptions);
    myParticipations = new LazyStore(
        () => this.api.userCompetitionParticipations.list(this.query), storeOptions);
    myVoteCodes = new LazyStore(
        () => this.api.voteCodes.list(this.query), storeOptions);
    myCodeRequests = new LazyStore(
        () => this.api.voteCodeRequests.list(this.query), storeOptions);
    myVotes = new LazyStore(
        () => this.api.userVotes.list(this.query), storeOptions);

    get eventId() {
        return this.event.id;
    }

    get eventURL() {
        return `/${this.eventId}`;
    }

    /** Get query parameters for fetching stuff related to this event. */
    protected get query() {
        return { event: this.eventId };
    }

    constructor(protected api: InstanssiREST, event: IEvent) {
        this.event = event;
   }

    /** Get a compo's votes object, if one exists. */
    getCompoVotes(compo: ICompo) {
        const allVotes = this.myVotes.value;
        return allVotes && allVotes.find(vote => vote.compo === compo.id);
    }

    /** Check if the user has already voted. */
    hasVotedInCompo(compo: ICompo): boolean {
        const compoVotes = this.getCompoVotes(compo);
        return compoVotes ? compoVotes.entries.length > 0 : false;
    }

    @computed
    get voteCodeRequests() {
        // Should only have one of these active per event.
        return this.myCodeRequests.value;
    }

    /**
     * True if the current user has no vote code for the event.
     */
    @computed
    get noVoteCode() {
        const { value } = this.myVoteCodes;
        const { voteCodeRequests } = this;

        const hasOkRequest = voteCodeRequests && voteCodeRequests.find(vc => {
            return vc.status === 1;
        });

        return !(value && value.length) && !hasOkRequest;
    }

    get hasEnded() {
        // HACK: Events have no end date, so assume they last a week.
        // Could compute it from compos, competitions and programme I guess.
        return moment().isAfter(moment(this.event.date).add(1, 'week'));
    }

    getCompoURL(compo: ICompo) {
        return `${this.eventURL}/compo/${compo.id}`;
    }

    getCompoVoteURL(compo: ICompo) {
        return `${this.eventURL}/compo/${compo.id}/vote`;
    }

    getCompoEntryAddURL(compo: ICompo) {
        return this.getCompoURL(compo) + '/entries/add';
    }

    getCompoEntryURL(compo: ICompo, entry: ICompoEntry) {
        return this.getCompoURL(compo) + '/entries/' + entry.id;
    }

    getCompoEntryEditURL(compo: ICompo, entry: ICompoEntry) {
        return this.getCompoURL(compo) + '/entries/edit/' + entry.id;
    }

    getProgrammeEventURL(progEvent: IProgrammeEvent) {
        return `${this.eventURL}/programme/${progEvent.id}`;
    }

    getCompetitionURL(competition: ICompetition) {
        return `${this.eventURL}/competition/${competition.id}`;
    }
}
