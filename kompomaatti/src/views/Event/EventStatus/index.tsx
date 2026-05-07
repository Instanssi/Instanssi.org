import React from 'react';
import { observer } from 'mobx-react';
import { computed, observable, action } from 'mobx';

import globalState from 'src/state';
import EventInfo from 'src/state/EventInfo';
import { L } from 'src/common';

import TicketCodeForm from './TicketCodeForm';
import RequestCodeForm from './RequestCodeForm';


enum NoCodeWorkflow {
    Info,
    TicketCode,
    RequestCode,
    RequestOk,
}

/**
 * Displays information about the current user's ability to participate in the event:
 * - Non-logged in users get told to go log in
 * - Logged in users with no vote code are instructed to enter it
 * - Lost users with no ticket are told to explain themselves and request a code
 * - Users with a pending request are told to wait warmly
 * - etc.
 */
@observer
export default class EventStatus extends React.Component<{
    event: EventInfo;
    /** Show this even if the event has ended or the user has a vote code? */
    showIfIrrelevant?: boolean;
}> {
    @observable noCodeMode = NoCodeWorkflow.Info;

    @computed
    get notLoggedIn() {
        return !globalState.user;
    }


    render() {
        const { notLoggedIn } = this;
        const { event, showIfIrrelevant } = this.props;
        const { noVoteCode, hasEnded } = event;

        if (hasEnded && !showIfIrrelevant) {
            return null;
        }

        if (hasEnded) {
            return this.renderEventOver();
        }

        if (globalState.userStore.isPending) {
            // Don't render anything if the user is unknown at this time.
            return null;
        }
        if (event.myVoteCodes.isPending) {
            // Don't render anything if the vote code status is unknown.
            return null;
        }
        if (event.myCodeRequests.isPending) {
            // yarp.
            return null;
        }

        // FIXME: If the "current" event has clearly ended, inform the user
        // about that before checking login or vote codes.
        let content;

        if (notLoggedIn) {
            content = this.renderNoLogin();
        } else if (noVoteCode) {
            content = this.renderNoVoteCode();
        } else if (showIfIrrelevant) {
            content = this.renderVoteOk();
        }

        return (
            <div className="frontpage-status">
                {content}
            </div>
        );
    }

    renderNoLogin() {
        return (
            <div className="alert alert-info">
                <span className="fa fa-info-circle" />&ensp;
                <L text="dashboard.notLoggedIn" />
                <hr />
                <div>
                    <a href="/users/login" className="btn btn-primary">
                        <L text="session.login" />
                    </a>
                </div>
            </div>
        );
    }

    @action.bound
    refreshRequests() {
        const { event } = this.props;
        return Promise.all([
            event.myVoteCodes.refresh(),
            event.myCodeRequests.refresh(),
        ]);
    }

    @action.bound
    resetCodeMode() {
        this.noCodeMode = NoCodeWorkflow.Info;
    }

    @action.bound
    showTicketCodeForm() {
        this.noCodeMode = NoCodeWorkflow.TicketCode;
    }

    @action.bound
    showCodeRequestForm() {
        this.noCodeMode = NoCodeWorkflow.RequestCode;
    }

    @action.bound
    handleCodeRequestSubmit() {
        this.noCodeMode = NoCodeWorkflow.RequestOk;
    }

    renderNoVoteCode() {
        const { noCodeMode } = this;
        const { voteCodeRequests } = this.props.event;
        const hasCodeRequest = voteCodeRequests && voteCodeRequests.length > 0;

        const hasRejectedRequest = voteCodeRequests && voteCodeRequests.find(vc => {
            return vc.status === 2;
        });

        return (
            <div className="alert alert-info">
                {!hasCodeRequest
                    ? <>
                        <h4>
                            <span className="fa fa-info-circle" />&ensp;
                        <L text="voteCode.missing" />
                        </h4>
                        <p><L text="voteCode.help" /></p>
                    </>
                    : <>
                        <h4>
                            <span className="fa fa-info-circle" />&ensp;
                        <L text="voteCode.requestPending" />
                        </h4>
                        <p>
                            {!hasRejectedRequest
                                ? <L text="voteCode.requestPendingHelp" />
                                : <L text="voteCode.requestRejectedHelp" />}
                        </p>
                    </>}
                <hr />
                {(noCodeMode === NoCodeWorkflow.Info) && (<div>
                    <button
                        type="button"
                        className="btn btn-primary"
                        onClick={this.showTicketCodeForm}
                    >
                        <L text="voteCode.useTicketCode" />
                    </button>
                    &ensp;
                    <button
                        type="button"
                        className="btn btn-link"
                        onClick={this.showCodeRequestForm}
                    >
                        <L text="voteCode.noTicketCode" />
                    </button>
                </div>)}
                {(noCodeMode === NoCodeWorkflow.TicketCode) && (
                    <TicketCodeForm
                        event={this.props.event}
                        onSubmit={this.resetCodeMode}
                        onCancel={this.resetCodeMode}
                    />
                )}
                {(noCodeMode === NoCodeWorkflow.RequestCode) && (
                    <RequestCodeForm
                        event={this.props.event}
                        onSubmit={this.handleCodeRequestSubmit}
                        onCancel={this.resetCodeMode}
                    />
                )}
            </div>
        );
    }

    renderVoteOk() {
        return (
            <div className="alert alert-info">
                <span className="fa fa-check" />&ensp;
                <L text="voteCode.hasCodeForEvent" />
            </div>
        );
    }

    renderEventOver() {
        return (
            <div className="alert alert-info">
                <L text="event.isOver" />
            </div>
        );
    }
}
