import React from 'react';
import { computed } from 'mobx';
import { observer } from 'mobx-react';
import { Link } from 'react-router-dom';
import moment from 'moment';

import { ICompo } from 'src/api/interfaces';
import EventInfo from 'src/state/EventInfo';
import { FormatTime, L } from 'src/common';
import globalState from 'src/state';

import './compositem.scss';

/** It's happening! */
interface ICompoHappening {
    time: moment.Moment;
    textKey: string;
    humanTime: JSX.Element;
}

/**
 * Displays a single compo in an event overview's compos list.
 *
 * Possibly with controls and other info.
 */
@observer
export class EventComposItem extends React.Component<{
    eventInfo: EventInfo;
    compo: ICompo;
}> {
    @computed
    get times() {
        const {
            voting_end,
            voting_start,
            adding_end,
            editing_end,
            compo_start,
        } = this.props.compo;
        return {
            votingEnd: moment(voting_end),
            votingStart: moment(voting_start),
            addingEnd: moment(adding_end),
            editingEnd: moment(editing_end),
            compoStart: moment(compo_start),
        };
    }

    @computed
    get nextCompoEvent(): ICompoHappening | null {
        const { timeMin } = globalState;
        const { compo } = this.props;
        const { is_votable } = compo;

        const { times } = this;

        function event(time: moment.Moment, textKey: string): ICompoHappening {
            return {
                time,
                textKey,
                humanTime: <FormatTime value={time} format="ddd LT" />,
            };
        }
        if (times.addingEnd.isAfter(timeMin)) {
            return event(times.addingEnd, 'compo.addingEnd');
        }
        if (times.editingEnd.isAfter(timeMin)) {
            return event(times.editingEnd, 'compo.editingEnd');
        }
        if (times.compoStart.isAfter(timeMin)) {
            return event(times.compoStart, 'compo.compoStart');
        }
        if (is_votable && times.votingStart.isAfter(timeMin)) {
            return event(times.votingStart, 'compo.votingStart');
        }
        if (is_votable && times.votingEnd.isAfter(timeMin)) {
            return event(times.votingEnd, 'compo.votingEnd');
        }
        return null;
    }

    @computed
    get votingIsOpen() {
        const { timeMin } = globalState;
        const { compo } = this.props;
        const { times } = this;
        const { is_votable } = compo;

        return (
            is_votable &&
            (times.votingStart.isSameOrBefore(timeMin) &&
                times.votingEnd.isAfter(timeMin))
        );
    }

    render() {
        const { user } = globalState;
        const { nextCompoEvent, votingIsOpen } = this;
        const { compo, eventInfo } = this.props;

        const hasVoteCode = !eventInfo.noVoteCode;

        const hasVoted = eventInfo.hasVotedInCompo(compo);

        return (
            <li key={compo.id} className="compos-item">
                <span className="item-time">
                    <FormatTime value={compo.compo_start} format="ddd LT" />
                </span>{' '}
                <span className="item-title">
                    <span className="item-title-info">
                        <div>
                            <Link to={eventInfo.getCompoURL(compo)}>
                                {compo.name}
                            </Link>
                        </div>
                        {nextCompoEvent && (
                            <div>
                                <L text={nextCompoEvent.textKey} />
                                {': '}
                                {nextCompoEvent.humanTime}
                            </div>
                        )}
                    </span>
                    <span className="item-title-actions">
                        {user && votingIsOpen && hasVoteCode && (
                            <span className="item-action">
                                {hasVoted && (
                                    <>
                                        <span
                                            className="fa fa-fw
                                        fa-check"
                                        />{' '}
                                    </>
                                )}
                                <Link to={eventInfo.getCompoVoteURL(compo)}>
                                    <L text="compo.vote" />
                                </Link>
                            </span>
                        )}
                    </span>
                </span>
                {/*
                    Accepting entries until 123123
                    Voting open!
                    Voted!
                    1 entry by (you)
                    Entries closed
                    Compo soon(tm)
                    Results @ Sun 1:00 PM
                */}
            </li>
        );
    }
}
