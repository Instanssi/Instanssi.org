import React from 'react';
import { observer } from 'mobx-react';
import { observable, action } from 'mobx';
import { Link, withRouter, RouteComponentProps } from 'react-router-dom';
import classNames from 'classnames';

import { L } from 'src/common';
import globalState from 'src/state';
import LanguageSwitch from '../LanguageSwitch';

import UserMenu from '../UserMenu';
import NavLink from './NavLink';
import { ActivityCube } from './Cube';

@observer
export class Header extends React.Component<RouteComponentProps<any>> {
    @observable isOpen = false;

    @action.bound
    toggleOpen() {
        this.isOpen = !this.isOpen;
    }

    render() {
        const { currentEvent } = globalState;

        return (
            <nav className="navbar navbar-inverse">
                <div className="navbar-header">
                    <button
                        type="button"
                        onClick={this.toggleOpen}
                        className={classNames(
                            'navbar-toggle',
                            { collapsed: !this.isOpen },
                        )}
                    >
                        <span className="fa fa-bars" />
                    </button>
                    <Link to="/" className="navbar-brand">
                        Kompomaatti
                        &ensp;
                        <ActivityCube />
                    </Link>
                    <span className="liability-reducer">
                        RC1
                    </span>
                </div>
                <div
                    className={classNames(
                        'collapse navbar-collapse',
                        { in: this.isOpen },
                    )}
                >
                    <ul className="nav navbar-nav">
                        {currentEvent && (
                            <NavLink to={currentEvent.eventURL}>
                                {currentEvent.event.name}
                            </NavLink>
                        )}
                        <NavLink to="/events" exact>
                            <L text="nav.events" />
                        </NavLink>
                    </ul>
                    <ul className="nav navbar-nav navbar-right">
                        <UserMenu />
                    </ul>
                    <div className="navbar-form navbar-right">
                        <div className="form-group">
                            <LanguageSwitch />
                        </div>
                    </div>
                </div>
            </nav>
        );
    }
}

export default withRouter(Header);
