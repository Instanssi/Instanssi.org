import React from 'react';
import { observer } from 'mobx-react';
import { computed } from 'mobx';
import _orderBy from 'lodash/orderBy';

import { LoadingWrapper, NoResults } from 'src/common';
import EventInfo from 'src/state/EventInfo';
import { EventComposItem } from './EventComposItem';

/**
 * Lists an event's compos.
 */
@observer
export default class EventCompos extends React.Component<{
    eventInfo: EventInfo;
}> {
    get compos() {
        return this.props.eventInfo.compos;
    }

    @computed
    get sortedCompos() {
        const { value } = this.compos;
        return value && _orderBy(value, compo => compo.compo_start);
    }

    render() {
        const { eventInfo } = this.props;
        const compos = this.sortedCompos;

        return (
            <LoadingWrapper store={this.compos}>
                <ul className="list-k event-compos">
                    {(compos && compos.length > 0)
                        ? compos.map(compo => (
                            <EventComposItem
                                key={compo.id}
                                compo={compo}
                                eventInfo={eventInfo}
                            />
                        ))
                        : <li><NoResults /></li>
                    }
                </ul>
            </LoadingWrapper>
        );
    }
}
