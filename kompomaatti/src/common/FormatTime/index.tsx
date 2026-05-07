import React from 'react';
import { observer } from 'mobx-react';
import { computed } from 'mobx';

import moment from 'moment';
import globalState from 'src/state';

export interface IFormatTimeProps {
    value: number | Date | moment.Moment | string | null;
    format?: string;
    locale?: string;
    placeholder?: string | any;
}

/**
 * Takes a ISO 8601 or JS Unix milliseconds timestamp as 'value'
 * and formats it. Can be customized by passing:
 * - 'format': Moment.js format string. Defaults to 'LLL'.
 * - 'locale': Moment locale id. Defaults to global locale or 'en'.
 */
@observer
export default class FormatTime extends React.Component<IFormatTimeProps> {
    @computed
    get formatted() {
        const { value, placeholder, locale, format } = this.props;
        if (!value) {
            return placeholder || '-';
        }
        return globalState.getMoment(value)
            .locale(locale || globalState.momentLocale || 'en')
            .format(format || 'LLL');
    }

    render() {
        return this.formatted;
    }
}
