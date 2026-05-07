import React from 'react';
import { computed, action } from 'mobx';
import { observer } from 'mobx-react';
import moment from 'moment';

import L from '../L';

import './timezone.scss';
import globalState from 'src/state';

/**
 * Shows the UTC offset used to display times-of-day for a specific date.
 *
 * The date is required because of daylight savings time.
 *
 * @todo Allow switching the time zone to the party time via this?
 */
@observer
export class TimeZoneIndicator extends React.Component<{
    time: string | number | moment.Moment | Date | null;
}> {
    @computed
    get offsetHours() {
        const { time } = this.props;
        if (!time) {
            return null;
        }
        const offsetHours = globalState.getMoment(time).utcOffset() / 60;
        return offsetHours;
    }

    @action.bound
    toggleZone() {
        if (globalState.tzOverride === null) {
            globalState.tzOverride = globalState.partyTimeZone;
        } else {
            globalState.tzOverride = null;
        }
    }

    render() {
        const { offsetHours } = this;

        if (offsetHours === null) {
            return null;
        }
        const offsetStr = offsetHours >= 0 ? `+${offsetHours}` : `${offsetHours}`;

        const helpTitle = globalState.tzOverride === null
            ? L.getText('timeZone.yourTZ')
            : L.getText('timeZone.partyTZ', { name: globalState.tzOverride });

        return (
            <span
                role="button"
                className="timezone-indicator"
                title={helpTitle}
                onClick={this.toggleZone}
            >
                <span className="fa fa-clock-o" />
                {' '}
                UTC{offsetStr}
            </span>
        );
    }
}
