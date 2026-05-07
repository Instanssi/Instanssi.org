import React from 'react';
import { observer } from 'mobx-react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';

import globalState from 'src/state';
import { L, LoadingWrapper } from 'src/common';

import EventStatus from '../Event/EventStatus';
/*
import FrontEvent from './FrontEvent';
import FrontProgramme from './FrontProgramme';
import FrontCompos from './FrontCompos';
import FrontCompetitions from './FrontCompetitions';
*/
import FrontSchedule from './FrontSchedule';

import './frontpage.scss';


@observer
export default class FrontPageView extends React.Component<any> {
    get currentEvent() {
        return globalState.currentEvent;
    }

    render() {
        const { currentEvent } = globalState;

        return (
            <div className="frontpage-view">
                <h1>Kompomaatti</h1>
                <p><L text="dashboard.welcome" /></p>
                <LoadingWrapper store={globalState.events}>
                    {currentEvent && <>
                        <Helmet>
                            <title>{L.getText('common.schedule')}</title>
                        </Helmet>

                        <h2>{currentEvent.event.name}</h2>
                        <div>
                            <Link to={currentEvent.eventURL} className="btn btn-link">
                                <span className="fa fa-calendar" />
                                &ensp;
                                <L text="event.linkTo" />
                            </Link>
                        </div>
                        <EventStatus event={currentEvent} />
                        <FrontSchedule eventInfo={currentEvent} />
                    </>}
                </LoadingWrapper>
            </div>
        );
    }
}
