import React from 'react';
import { observer } from 'mobx-react';

import { L } from 'src/common';

import EventCompos from './EventCompos';
import EventCompetitions from './EventCompetitions';
import EventProgramme from './EventProgramme';
import EventInfo from '../../../state/EventInfo';


@observer
export default class EventOverview extends React.Component<{
    eventInfo: EventInfo;
}> {
    componentDidMount() {
        this.props.eventInfo.compos.refresh();
    }

    render() {
        const { eventInfo } = this.props;

        return (
            <div className="event-overview">
                <h2><L text="event.compos" /></h2>
                <EventCompos eventInfo={eventInfo} />

                <h2><L text="event.competitions" /></h2>
                <EventCompetitions eventInfo={eventInfo} />

                <h2><L text="event.programme" /></h2>
                <EventProgramme eventInfo={eventInfo} />
            </div>
        );
    }
}
