import React from 'react';
import { observer } from 'mobx-react';
import { action, observable } from 'mobx';
import moment from 'moment';

/**
 * Displays current time to or from a given date.
 */
@observer
export default class FormatDuration extends React.Component<{
    to: Date | string | moment.Moment;
}> {
    @observable now = new Date();
    @observable diff: number;

    protected timeout = null as any;

    componentDidMount() {
        this.refresh();
    }

    componentWillUnmount() {
        clearTimeout(this.timeout);
    }

    get toDate() {
        const { to } = this.props;
        if (typeof to === 'string') {
            return new Date(to);
        }
        return to;
    }

    @action
    refresh() {
        this.now = new Date();
        // TODO: Set the timeout so that the duration
        // refreshes at some suitable rate depending on how much time is left:

        const toMillis = this.toDate.valueOf();
        const nowMillis = this.now.valueOf();
        const diff = toMillis - nowMillis;
        this.diff = diff;

        // If off by more than 3 minutes, only update once per minute.
        // Otherwise update once per second.
        const absDiffSecs = Math.abs(diff) / 1000;
        const nextTimeout = absDiffSecs > 180 ? (60 * 1000) : 1000;

        this.timeout = setTimeout(() => {
            this.refresh();
        }, nextTimeout);
    }

    render() {
        return moment.duration(this.diff).humanize();
    }
}
