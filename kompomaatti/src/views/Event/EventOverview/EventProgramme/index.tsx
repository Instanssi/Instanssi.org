import React from 'react';
import { observer } from 'mobx-react';
import { computed } from 'mobx';
import { Link } from 'react-router-dom';
import _orderBy from 'lodash/orderBy';

import { NoResults, LoadingWrapper, FormatTime } from 'src/common';
import EventInfo from 'src/state/EventInfo';
import { IProgrammeEvent } from 'src/api/interfaces';

/**
 * Lists an event's programme events.
 */
@observer
export default class EventProgramme extends React.Component<{
    eventInfo: EventInfo;
}> {
    get progEvents() {
        return this.props.eventInfo.programme;
    }

    @computed
    get sortedEvents() {
        const { value } = this.progEvents;
        return value && _orderBy(value, event => event.start);
    }

    render() {
        const { eventInfo } = this.props;
        const events = this.sortedEvents;

        const hasContent = (pe: IProgrammeEvent) => !!(pe.description || pe.presenters);

        return (
            <LoadingWrapper store={this.progEvents}>
                <ul className="list-k">
                    {(events && events.length > 0)
                        ? events.map(event => (
                            <li key={event.id} className="programme-item">
                                <span className="item-time">
                                    <FormatTime value={event.start} format="ddd LT" />
                                </span>
                                {' '}
                                {hasContent(event)
                                    ? (
                                        <Link
                                            className="item-title"
                                            to={eventInfo.getProgrammeEventURL(event)}
                                        >
                                            {event.title}
                                        </Link>
                                    ) : <span>{event.title}</span>
                                }
                            </li>
                        ))
                        : <li><NoResults /></li>
                    }
                </ul>
            </LoadingWrapper>
        );
    }
}
