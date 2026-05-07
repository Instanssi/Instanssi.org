import React from 'react';
import { observer } from 'mobx-react';
import { computed } from 'mobx';
import { withRouter, RouteComponentProps } from 'react-router';
import { Helmet } from 'react-helmet';

import { FormatTime, LoadingWrapper, L } from 'src/common';

import EventInfo from 'src/state/EventInfo';
import CompetitionStatus from './CompetitionStatus';
import CompetitionResults from './CompetitionResults';


/**
 * Displays details of a single competition within a party event.
 */
@observer
export class EventCompetition extends React.Component<{
    eventInfo: EventInfo;
} & RouteComponentProps<{ cmpId: string }>> {
    @computed
    get competition() {
        const { idParsed } = this;
        const competitions = this.props.eventInfo.competitions.value;
        return competitions && competitions.find(c => c.id === idParsed);
    }

    get idParsed() {
        return Number.parseInt(this.props.match.params.cmpId, 10);
    }

    @computed
    get descriptionHTML() {
        const { competition } = this;
        return competition ? {
            __html: competition.description || '-',
        } : undefined;
    }

    render() {
        const { eventInfo } = this.props;
        const { competition } = this;

        return (
            <LoadingWrapper
                className="event-competition"
                store={this.props.eventInfo.competitions}
            >
                {competition && <>
                    <Helmet>
                        <title>{`${competition.name} @ ${eventInfo.event.name}`}</title>
                        <meta
                            property="og:title"
                            content={`${competition.name} @ ${eventInfo.event.name}`}
                        />
                    </Helmet>
                    <div className="competition-title">
                        <h2>{competition.name}</h2>
                        <p>
                            <FormatTime value={competition.start} format="LLL" />
                            {' - '}
                            <FormatTime value={competition.end} format="LT" />
                        </p>
                        <p>
                            <L text="competition.participationEnd" />
                            {': '}
                            <FormatTime value={competition.participation_end} format="LT" />
                        </p>
                    </div>
                    <CompetitionStatus
                        eventInfo={this.props.eventInfo}
                        competition={competition}
                    />
                    { competition.show_results && (
                        <CompetitionResults
                            eventInfo={this.props.eventInfo}
                            competition={competition}
                        />
                    )}
                    <h3><L text="common.description" /></h3>
                    <p
                        className="competition-description"
                        dangerouslySetInnerHTML={this.descriptionHTML}
                    />
                </>}
            </LoadingWrapper>
        );
    }
}

export default withRouter(EventCompetition);
