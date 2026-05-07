import React from 'react';
import { observer } from 'mobx-react';

import globalState from 'src/state';


const { translate } = globalState;

@observer
export default class NotLoggedIn extends React.Component<any> {
    render() {
        return (
            <div>
                <span className="fa fa-fw fa-info-circle" />
                {' '}
                {translate('common.notLoggedIn')}
            </div>
        );
    }
}
