// This file configures the application's main routes/views.

import React from 'react';
import { Switch, Route } from 'react-router-dom';
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import { RouteComponentProps, withRouter } from 'react-router';

import ErrorBoundary from 'src/common/ErrorBoundary';

import FrontPage from './FrontPage';
import EventsList from './EventsList';
import Event from './Event';

export class Views extends React.Component<RouteComponentProps<any>> {
    render() {
        const { location } = this.props;

        // fire transition only when the first path segment changes.
        // would this be cleaner if the transition was in the routed views instead?
        const locationKey = location.pathname.split('/')[1];

        return (
            <div id="views">
                <ErrorBoundary>
                    <TransitionGroup className="transition-group">
                        <CSSTransition key={locationKey} classNames="route" timeout={300}>
                            <Switch location={location}>
                                <Route exact path="/events"><EventsList /></Route>
                                <Route path="/:eventId"><Event /></Route>
                                <Route><FrontPage /></Route>
                            </Switch>
                        </CSSTransition>
                    </TransitionGroup>
                </ErrorBoundary>
            </div>
        );
    }
}

export default withRouter(Views);
