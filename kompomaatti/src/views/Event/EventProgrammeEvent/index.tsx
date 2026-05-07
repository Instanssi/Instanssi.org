import React from 'react';
import { observer } from 'mobx-react';
import { computed } from 'mobx';
import { withRouter, RouteComponentProps } from 'react-router';
import { Helmet } from 'react-helmet';

import { FormatTime, LoadingWrapper, L } from 'src/common';

import EventInfo from 'src/state/EventInfo';

/**
 * Displays details of a single programme event within a party event.
 */
@observer
export class EventProgrammeEvent extends React.Component<{
    eventInfo: EventInfo;
} & RouteComponentProps<{ progId: string }>> {
    @computed
    get progEvent() {
        const { idParsed } = this;
        const progEvents = this.props.eventInfo.programme.value;
        return progEvents && progEvents.find(pe => pe.id === idParsed);
    }

    get idParsed() {
        return Number.parseInt(this.props.match.params.progId, 10);
    }

    @computed
    get descriptionHTML() {
        const { progEvent } = this;
        return progEvent ? {
            __html: progEvent.description || '-',
        } : undefined;
    }

    render() {
        const { eventInfo } = this.props;
        const { progEvent } = this;

        return (
            <LoadingWrapper
                className="event-progevent"
                store={this.props.eventInfo.programme}
            >
                {progEvent && <>
                    <Helmet>
                        <title>{`${progEvent.title} @ ${eventInfo.event.name}`}</title>
                        <meta
                            name="description"
                            content={`${progEvent.title} @ ${eventInfo.event.name}`}
                        />
                        <meta
                            property="og:title"
                            content={`${progEvent.title} @ ${eventInfo.event.name}`}
                        />
                        {progEvent.description && progEvent.description.length > 0 && (
                            <meta
                                property="og:description"
                                content={progEvent.description}
                            />
                        )}
                    </Helmet>
                    <div className="progevent-title">
                        <h2>{progEvent.title}</h2>
                        { progEvent.end ? <p>
                            <FormatTime value={progEvent.start} format="LLL" />
                            {' - '}
                            <FormatTime value={progEvent.end} format="LT" />
                            {', '}
                            {progEvent.place}
                        </p> : <p>
                            <FormatTime value={progEvent.start} format="LLL" />
                            {progEvent.place && <>
                                {', '}
                                {progEvent.place}
                            </>}
                        </p>}
                    </div>
                    {progEvent.presenters && (<>
                        <h3><L text="programmeEvent.presenters" /></h3>
                        <p className="progevent-presenters">
                            {progEvent.presenters}
                            {!!progEvent.presenters_titles && <>
                                , {progEvent.presenters_titles}
                            </>}
                        </p>
                    </>)}
                    <h3><L text="common.description" /></h3>
                    <p
                        className="progevent-description"
                        dangerouslySetInnerHTML={this.descriptionHTML}
                    />
                </>}
            </LoadingWrapper>
        );
    }
}

export default withRouter(EventProgrammeEvent);
