import React from 'react';
import { computed } from 'mobx';
import { observer } from 'mobx-react';

import globalState from 'src/state';


@observer
export default class FormatNumber extends React.Component<{
    value: number | null | undefined,
    fallback?: string;
    options?: Intl.NumberFormatOptions,
    precision: number,
}> {
    @computed
    get formatter() {
        const { precision, options } = this.props;
        return new Intl.NumberFormat(globalState.momentLocale, {
            maximumFractionDigits: precision,
            minimumFractionDigits: precision,
            ...options,
        });
    }

    render() {
        const { value, fallback } = this.props;
        if (typeof value !== 'number') {
            return typeof fallback !== 'undefined' ? fallback : '-';
        }
        return this.formatter.format(value);
    }
}
