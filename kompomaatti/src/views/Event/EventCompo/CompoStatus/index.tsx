import React from 'react';
import { observer } from 'mobx-react';
import moment from 'moment';

import globalState from 'src/state';
import EventInfo from 'src/state/EventInfo';
import { LazyStore } from 'src/stores';

import { Link } from 'react-router-dom';
import { ICompo } from 'src/api/interfaces';
import { computed } from 'mobx';
import { FormatTime, L } from 'src/common';
import EventStatus from 'src/views/Event/EventStatus';


/**
 * Shows status info about a compo: timeframe, own entries, etc.
 *
 * @todo Merge the "compo actions" feature into this.
 */
@observer
export default class CompoStatus extends React.Component<{
    eventInfo: EventInfo;
    compo: ICompo;
}> {
    // Only fetch this if the user is logged in.
    store = new LazyStore(() => globalState.user ? globalState.api.userCompoEntries.list({
        event: this.props.eventInfo.eventId,
    }) : Promise.reject(null));

    @computed
    get ownEntries() {
        const ownEntries = this.store.value;
        const compoId = this.props.compo.id;
        return ownEntries ? ownEntries.filter(entry => entry.compo === compoId) : null;
    }

    @computed
    get schedule() {
        const { compo } = this.props;
        const parse = v => v ? moment(v) : null;

        // Could just map the compo JSON into something with these sooner.
        return {
            addingEnd: parse(compo.adding_end),
            editingEnd: parse(compo.editing_end),
            compoStart: parse(compo.compo_start),
            votingStart: parse(compo.voting_start),
            votingEnd: parse(compo.voting_end),
        };
    }

    /** Check if the compo is votable at all. */
    get isVotingEnabled() {
        const { compo } = this.props;
        return compo && compo.is_votable;
    }

    @computed
    get votingActive() {
        const { schedule } = this;
        const now = moment(globalState.timeSec);
        const { votingStart, votingEnd } = schedule;
        if (votingStart && votingEnd) {
            return now.isAfter(votingStart) && now.isBefore(votingEnd);
        }
        return false;
    }

    render() {
        return (
            <div className="compo-status">
                {this.renderSchedule()}
                {this.renderActions()}
            </div>
        );
    }

    renderSchedule() {
        const { schedule } = this;

        const scheduleField = (title, value) => (
            <li>
                <span className="item-time">
                    <FormatTime format="ddd" value={value} />
                    {' '}
                    <FormatTime format="LT" value={value} />
                </span>
                <L text={title} />
            </li>
        );

        return (
            <div>
                <h3><L text="common.schedule" /></h3>
                <ul className="list-k">
                    {scheduleField('compo.addingEnd', schedule.addingEnd)}
                    {scheduleField('compo.editingEnd', schedule.editingEnd)}
                    {scheduleField('compo.compoStart', schedule.compoStart)}
                    {scheduleField('compo.votingStart', schedule.votingStart)}
                    {scheduleField('compo.votingEnd', schedule.votingEnd)}
                </ul>
            </div>
        );
    }

    renderActions() {
        const { compo, eventInfo } = this.props;
        const { ownEntries, schedule } = this;
        const now = globalState.timeMin;

        const canAdd = schedule.addingEnd && schedule.addingEnd.isAfter(now);
        const canEdit = schedule.editingEnd && schedule.editingEnd.isAfter(now);
        const { votingActive } = this;
        const { noVoteCode } = eventInfo;
        const loggedIn = !!globalState.user;

        return (
            <div className="compo-status">
                {votingActive && <div className="alert alert-info">
                    <span className="fa fa-info-circle" />&ensp;
                        {loggedIn
                        ? <L text="compo.votingIsOpen" />
                        : <L text="compo.votingIsOpenNotLoggedIn" />
                    }
                    {(loggedIn && !noVoteCode) &&  <>
                        <hr />
                        <Link
                            className="btn btn-primary"
                            to={eventInfo.getCompoVoteURL(compo)}
                        >
                            <L text="compo.vote" />
                        </Link>
                    </>}
                    <div className="clearfix" />
                </div>}
                {loggedIn && <>
                    <h3><L text="compo.myEntries" /></h3>
                    {(ownEntries && ownEntries.length > 0) && (
                        <ul className="list-k">
                            {ownEntries.map(entry => (
                                <li key={entry.id}>
                                    <div className="item-time">
                                        {canEdit && (
                                            <Link to={eventInfo.getCompoEntryEditURL(compo, entry)}>
                                                <L text="common.edit" />
                                            </Link>
                                        )}
                                    </div>
                                    <div className="flex-fill">
                                        {entry.name}
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </>}
                {(canAdd && loggedIn) && <div>
                    <Link to={eventInfo.getCompoEntryAddURL(compo)} className="btn btn-primary">
                        <L text="compo.addEntry" />
                    </Link>
                </div>
                }
                {!loggedIn && (canAdd || canEdit) && <>
                    <div className="alert alert-info">
                        <span className="fa fa-info-circle" />&ensp;
                        <L text="compo.logInToAddEntries" />
                    </div>
                </>}
            </div >
        );
    }
}
