import React from 'react';

import classNames from 'classnames';

import { withRouter } from 'react-router';
import { Link } from 'react-router-dom';

interface INavLinkProps {
    to: string|object;
    replace?: boolean;
    exact?: boolean;
    strict?: boolean;

    // props from withRouter
    match?: any;
    location?: any;
}

/**
 * Renders a Bootstrap 4 nav link that lights up when its route matches.
 *
 * (TS typings for withRouter are slightly bugged)
 */
@(withRouter as any)
export default class NavLink extends React.Component<INavLinkProps> {
    get isActive() {
        const { exact, to, location } = this.props;
        // If the link is "exact", the nav link is active when the matched
        // path is exactly the "to" property.
        // If not, the link is active when the match path starts with props.to.
        return exact
            ? (location && to === location.pathname)
            : (location && location.pathname.indexOf(to) === 0);
    }

    render() {
        const { to, replace, children } = this.props;

        const active = this.isActive;

        const className = classNames(
            'nav-item',
            { active },
        );

        return (
            <li className={className}>
                <Link className="nav-link" to={to} replace={replace}>
                    {children}
                </Link>
            </li>
        );
    }
}
