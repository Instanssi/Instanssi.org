import React from 'react';
import { observer } from 'mobx-react';

import globalState from 'src/state';


const { translate } = globalState;

@observer
export default class UserMenu extends React.Component<any> {
    get user() {
        return globalState.user;
    }

    render() {
        const { user } = this;
        return (
            <li>
                {user ? (
                    <a href="/users/profile">
                        {user.first_name || user.email || '?'}
                    </a>
                ) : (
                    <a href="/users/login">
                        {translate('nav.login')}
                    </a>
                )}
            </li>
        );
    }
}
