import React from 'react';
import { observer } from 'mobx-react';
import { action, observable, runInAction, computed } from 'mobx';
import { Link } from 'react-router-dom';
import _orderBy from 'lodash/orderBy';
import _shuffle from 'lodash/shuffle';
import moment from 'moment';
import { Helmet } from 'react-helmet';
import { Prompt } from 'react-router';
import { SortableContainer, SortableElement, SortableHandle, arrayMove } from 'react-sortable-hoc';

import globalState from 'src/state';
import { LazyStore } from 'src/stores';
import { ICompo, ICompoEntry } from 'src/api/interfaces';
import EventInfo from 'src/state/EventInfo';
import { L, FormatNumber } from 'src/common';

import EntryModal from '../EntryModal';
import './vote.scss';
import { toast } from 'react-toastify';

const DragHandle = SortableHandle((props: {
    onTripleClick: () => void;
    onMoveUp: () => void;
    onMoveDown: () => void;
}) => {
    const onClick = React.useCallback((event: React.MouseEvent<any>) => {
        try {
            const count = event?.nativeEvent?.detail;
            if (typeof count === 'number' && count > 1) {
                props.onTripleClick();
            }
        } catch {
            // ... something happened?
        }
    }, [props.onTripleClick]);

    const onKeyDown = React.useCallback((event: React.KeyboardEvent<any>) => {
        switch (event.key) {
            case "ArrowUp": {
                event.preventDefault();
                props.onMoveUp();
                break;
            }
            case "ArrowDown": {
                event.preventDefault();
                props.onMoveDown();
                break;
            }
            default: /* */
        }
    }, [props.onMoveUp, props.onMoveDown]);

    return (
        <span className="item-handle" onMouseDown={onClick} onKeyDown={onKeyDown} tabIndex={0}>
            <span className="fa fa-sort" />
        </span>
    );
});

const VoteEntryItem = SortableElement((props: {
    value: ICompoEntry;
    num: string;
    pos: number | null;
    isAboveBar?: boolean;
    onShowDetails: (entry: ICompoEntry) => void;
    onMoveToTop: (entry: ICompoEntry) => void;
    onMoveBelow: (entry: ICompoEntry) => void;
    onMoveUp: (entry: ICompoEntry) => void;
    onMoveDown: (entry: ICompoEntry) => void;
}) => (
        <li className="voting-item">
            <div className="item-number">
                <div className="item-number-pos">
                    {props.num}&ensp;
                </div>
                <div className="item-number-score">
                    {typeof props.pos === 'number' &&
                        <>
                            <FormatNumber
                                value={1.0 / props.pos}
                                precision={2}
                            />
                            {' p'}
                        </>
                    }
                </div>
            </div>
            <div className="item-content">
                <div className="item-title">
                    {props.value.name} <span className="item-creator">by {props.value.creator}
                        {' '}
                        {/*({(props.value as any)._currentVote || '-'})*/}
                    </span>
                </div>
                <div className="item-actions">
                    {props.value.imagefile_thumbnail_url && (
                        <img
                            className="vote-thumbnail"
                            src={props.value.imagefile_thumbnail_url}
                            onClick={() => props.onShowDetails(props.value)}
                        />
                    )}
                    <button
                        className="btn btn-link"
                        type="button"
                        onClick={() => props.onShowDetails(props.value)}
                        title={L.getText('common.showDetails')}
                    >
                        <span className="fa fa-fw fa-info-circle" />
                    </button>
                </div>
            </div>
            <DragHandle
                onTripleClick={() => props.isAboveBar ? props.onMoveBelow(props.value) : props.onMoveToTop(props.value)}
                onMoveUp={() => props.onMoveUp(props.value)}
                onMoveDown={() => props.onMoveDown(props.value)}
            />
        </li>
    ));

const VoteDivider = SortableElement((props: { entryIds: number[] }) => (
    <li className="voting-item divider">
        <L text="voting.divider" />
    </li>
));

const VoteEntryList = SortableContainer((props: {
    items: Array<ICompoEntry | null>;
    entryIds: number[];
    isLocked?: boolean;
    onShowDetails: (entry: ICompoEntry) => any;
    /** Called when an entry wants to move to the top. */
    onMoveToTop: (index: number, entry: ICompoEntry) => void;
    /** Called when an entry wants to move below the bar. */
    onMoveBelow: (index: number, entry: ICompoEntry) => void;
    /** Called when an entry wants to move up. */
    onMoveUp: (index: number, entry: ICompoEntry) => void;
    /** Called when an entry wants to move down. */
    onMoveDown: (index: number, entry: ICompoEntry) => void;
}) => {
    const { items, entryIds, isLocked } = props;
    let foundDivider = false;
    return (
        <ul className="list-k">
            {items.map((value, index: number) => {
                if (!value) {
                    foundDivider = true;
                    return <VoteDivider key="_divider" index={index} entryIds={entryIds} />;
                }
                return (
                    <VoteEntryItem
                        disabled={!value || isLocked}
                        key={value.id}
                        index={index}
                        value={value}
                        onShowDetails={props.onShowDetails}
                        isAboveBar={!foundDivider}
                        onMoveToTop={() => props.onMoveToTop(index, value)}
                        onMoveBelow={() => props.onMoveBelow(index, value)}
                        onMoveUp={() => props.onMoveUp(index, value)}
                        onMoveDown={() => props.onMoveDown(index, value)}
                        num={foundDivider ? '-' : `${index + 1}.`}
                        pos={!foundDivider ? (index + 1) : null}
                    />
                );
            })}
        </ul>
    );
});

@observer
export default class CompoVote extends React.Component<{
    eventInfo: EventInfo;
    compo: ICompo;
}> {
    compoEntries = new LazyStore(() => globalState.api.compoEntries.list({
        compo: this.props.compo.id,
    }));

    /** Has the user made changes to the votes? */
    @observable hasChanges = false;
    /** Is this trying to send vote changes right now? */
    @observable isSubmitting = false;
    /** Show detailed info for an entry? */
    @observable.ref showDetailsFor: ICompoEntry | null = null;

    /** In-view state. */
    @observable.ref votes: number[] = [];
    @observable.ref entries: ICompoEntry[] = [];

    /** Items ordered by votes. */
    @observable.shallow items: Array<ICompoEntry | null> = [];

    disposers: any[] = [];

    componentDidMount() {
        this.refresh();
    }

    componentWillUnmount() {
        this.disposers.forEach(d => d());
    }

    /**
     * Fetch new info on the compo's entries list and the user's votes
     */
    refresh() {
        const { compo, eventInfo } = this.props;
        return Promise.all([
            // Let's just fetch all the votes now.
            eventInfo.myVotes.refresh(),
            // Make sure we have up-to-date info on the compo's entries.
            this.compoEntries.refresh(),
        ]).then(([allVotes, entries]) => runInAction(() => {
            const votes = allVotes.filter(userVote => userVote.compo === compo.id);
            this.votes = (votes && votes.length > 0) ? votes[0].entries : [];
            this.entries = _shuffle(entries);
            this.entries.forEach(e => {
                (e as any)._currentVote = this.votes.findIndex(v => v === e.id) + 1;
            });
            this.init();
        }));
    }

    /**
     * Initialize the sortable compo entries list.
     */
    @action
    init() {
        const { votes } = this;

        const voteIndex = {};
        votes.forEach((entryId, index) => {
            voteIndex[entryId] = index;
        });

        const filtered = this.entries.filter(entry => !entry.disqualified);

        const withDivider: Array<ICompoEntry | null> = filtered;
        withDivider.push(null);

        this.items = _orderBy(withDivider, (entry, index) => {
            if (entry === null) {
                return 9000;
            }
            // Order the list of entries and null divider so that entries already
            // voted for are positioned according to their index in the votes list.
            // The divider is placed after that, and then the remaining entries
            // are listed in their shuffled order.
            const pos = voteIndex[entry.id];
            if (typeof pos === 'number') {
                return pos;
            }
            return 9001 + index;
        });
    }

    @computed
    get entryIds() {
        const entryIds: number[] = [];
        for (const entry of this.items) {
            if (entry) {
                entryIds.push(entry.id);
            } else {
                break;
            }
        }
        return entryIds;
    }

    @action.bound
    handleSubmit(event) {
        event.preventDefault();
        const { entryIds } = this;

        if (!entryIds.length || this.isSubmitting) {
            return Promise.reject(null);
        }

        this.isSubmitting = true;

        return globalState.api.userVotes.setVotes({
            compo: this.props.compo.id,
            entries: entryIds,
        }).then(
            () => runInAction(() => {
                this.hasChanges = false;
                this.isSubmitting = false;
                toast.success(<L text="voting.saveOk" />);
                this.refresh();
            }),
            (error) => runInAction(() => {
                toast.error(<L text="voting.saveFail" />);
                this.isSubmitting = false;
            }),
        );
    }

    @action.bound
    onSortEnd({ oldIndex, newIndex }) {
        this.hasChanges = true;
        this.items = arrayMove(this.items, oldIndex, newIndex);
    }

    /**
     * Move an entry to the top.
     * @param index Entry index to move.
     */
    @action.bound
    moveToTop(index: number) {
        this.items = arrayMove(this.items, index, 0);
    }

    /**
     * Drop an entry below the bar.
     * @param index Entry index to move.
     */
    @action.bound
    moveBelow(index: number) {
        this.items = arrayMove(this.items, index, this.items.length - 1);
    }

    @action.bound
    moveUp(index: number) {
        // If the index isn't at the top yet, swap the item and the one immediately above it
        if (index > 0) {
            this.items = arrayMove(this.items, index, index - 1);
        }
    }

    @action.bound
    moveDown(index: number) {
        if (index < this.items.length - 1) {
            this.items = arrayMove(this.items, index, index + 1);
        }
    }

    @computed
    get isVotable() {
        return this.props.compo.is_votable;
    }

    @computed
    get votingStart() {
        return moment(this.props.compo.voting_start);
    }

    @computed
    get votingEnd() {
        return moment(this.props.compo.voting_end);
    }

    @computed
    get canVote() {
        const { isVotable, votingEnd, votingStart } = this;
        const { timeMin } = globalState;
        const now = moment(timeMin);
        const voteTime = now.isSameOrAfter(votingStart) && now.isBefore(votingEnd);
        return globalState.user && isVotable && voteTime;
    }

    @action.bound
    openEntryDetails(entry: ICompoEntry) {
        this.showDetailsFor = entry;
    }

    @action.bound
    hideEntryDetails() {
        this.showDetailsFor = null;
    }

    render() {
        const { entryIds, hasChanges } = this;

        const deadline = globalState.getMoment(this.props.compo.voting_end)
            .locale(globalState.momentLocale);
        const ended = deadline.isBefore(globalState.timeMin);

        return (
            <div className="compo-vote">
                <Helmet>
                    {/* This page might not be available later. */}
                    <meta name="googlebot" content="noindex" />
                </Helmet>
                {<Prompt
                    when={hasChanges}
                    message={L.getText('voting.leaveWithoutSaving')}
                />}
                <h3><L text="compo.vote" /></h3>
                {!ended ? <div className="alert alert-info">
                    <span className="fa fa-clock-o" />&ensp;
                    <L
                        text="voting.deadline"
                        values={{
                            date: deadline.format('ddd LLL'),
                        }}
                    />
                </div> : <div className="alert alert-info"><L text="voting.ended" /></div>}
                <form onSubmit={this.handleSubmit}>
                    <ul>
                        <li>
                            <L text="voting.help" />
                            <span className="fa fa-sort" />
                            {'. '}
                            <L text="voting.help2" />
                        </li>
                        <li>
                            <L text="voting.quickMoveHelp" />
                            <span className="fa fa-sort" />
                            {'. '}
                        </li>
                        <li>
                            <L text="voting.help3" />
                            <span className="fa fa-info-circle" />
                            {'.'}
                        </li>
                    </ul>
                    {entryIds.length === 0 && (
                        <div className="voting-item placeholder">
                            <L text="voting.placeholder" />
                        </div>
                    )}
                    <VoteEntryList
                        items={this.items}
                        onSortEnd={this.onSortEnd}
                        entryIds={entryIds}
                        isLocked={!this.canVote}
                        onShowDetails={this.openEntryDetails}
                        onMoveToTop={this.moveToTop}
                        onMoveBelow={this.moveBelow}
                        onMoveUp={this.moveUp}
                        onMoveDown={this.moveDown}
                        lockAxis="y"
                        useDragHandle
                    />
                    <div>
                        <button
                            className="btn btn-primary"
                            disabled={entryIds.length <= 0 || this.isSubmitting}
                        >
                            <L text="common.save" />
                        </button>
                        &ensp;
                        {this.isSubmitting && <span className="fa fa-fw fa-spin fa-spinner" />}
                        <Link
                            className="btn btn-link"
                            to={this.props.eventInfo.eventURL}
                        >
                            <L text="voting.backToEvent" />
                        </Link>
                    </div>
                    <p>
                        {entryIds.length > 0
                            ? <span>{hasChanges && <L text="voting.hasChanges" />}</span>
                            : <span><L text="voting.atLeastOneRequired" /></span>
                        }
                    </p>
                </form>
                {this.showDetailsFor && <EntryModal
                    entry={this.showDetailsFor}
                    onClose={this.hideEntryDetails}
                />}
            </div>
        );
    }
}
