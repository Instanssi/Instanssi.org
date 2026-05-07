import React from 'react';
import { observer } from 'mobx-react';

import globalState from 'src/state';


/** Translate some text. */
@observer
export default class L extends React.Component<{
    text: string;
    values?: any;
}> {
    static getText(text: string, values?: any) {
        return globalState.translate(text, values) || `[${text}]`;
    }

    render() {
        const { text, values } = this.props;
        // This accesses observable state, so the component ends up observing it.
        return L.getText(text, values);
    }
}
