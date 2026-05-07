import React from 'react';
import { computed } from 'mobx';
import { observer } from 'mobx-react';
import { Switch, Route, withRouter, RouteComponentProps } from 'react-router';
import { Link, Redirect } from 'react-router-dom';
import { Helmet } from 'react-helmet';

import { FormatTime, LoadingWrapper } from 'src/common';

import EventInfo from 'src/state/EventInfo';

import CompoEntry from './CompoEntry';
import CompoEntryAdd from './CompoEntryAdd';
import CompoEntryEdit from './CompoEntryEdit';
import CompoOverview from './CompoOverview';
import CompoVote from './CompoVote';

/**
 * Displays details of a single compo within an event.
 */
@observer
export class EventCompo extends React.Component<{
    eventInfo: EventInfo;
} & RouteComponentProps<{ compoId: string }>> {

    componentDidMount() {
        // Ugh, the schedule is changing too fast.
        // Force refresh the compo info when viewing any individual compo.
        this.props.eventInfo.compos.refresh();
    }

    @computed
    get compo() {
        const compos = this.props.eventInfo.compos.value;
        const { idParsed } = this;
        return compos && compos.find(compo => compo.id === idParsed);
    }

    get idParsed() {
        return Number.parseInt(this.props.match.params.compoId, 10);
    }

    render() {
        const { eventInfo } = this.props;
        const { compo } = this;
        const { url } = this.props.match;

        if (!eventInfo.compos.isPending && !compo) {
            return <Redirect to={eventInfo.eventURL} />;
        }

        return (
            <LoadingWrapper
                className="event-compo"
                store={eventInfo.compos}
            >
                {compo && <>
                    <Helmet>
                        <title>{`${compo.name} @ ${eventInfo.event.name}`}</title>
                        <meta
                            property="og:title"
                            content={`${compo.name} @ ${eventInfo.event.name}`}
                        />
                        <meta
                            name="description"
                            content={compo.name}
                        />
                        {/* (description left out because it's often HTML soup, yay) */}
                    </Helmet>
                    <div className="compo-title">
                        {/* Make the title a link, but only when not on the same page
                        (could and probably should make a general solution for this) */}
                        <Switch>
                            <Route exact path={url}>
                                <h2>{compo.name}</h2>
                            </Route>
                            <Route>
                                <h2>
                                    <Link to={eventInfo.getCompoURL(compo)}>
                                        {compo.name}
                                    </Link>
                                </h2>
                            </Route>
                        </Switch>
                        <p><FormatTime value={compo.compo_start} /></p>
                    </div>
                    <Switch>
                        <Route exact path={url + '/entries/add'}>
                            <CompoEntryAdd
                                eventInfo={eventInfo}
                                compo={compo}
                            />
                        </Route>
                        <Route exact path={url + '/entries/edit/:entryId'}>
                            <CompoEntryEdit
                                eventInfo={eventInfo}
                                compo={compo}
                            />
                        </Route>
                        <Route path={url + '/entries/:entryId'}>
                            <CompoEntry
                                eventInfo={eventInfo}
                                compo={compo}
                            />
                        </Route>
                        <Route exact path={url + '/vote'}>
                            <CompoVote
                                eventInfo={eventInfo}
                                compo={compo}
                            />
                        </Route>
                        <Route>
                            <CompoOverview
                                compo={compo}
                                eventInfo={eventInfo}
                            />
                        </Route>
                    </Switch>
                </>}
            </LoadingWrapper>
        );
    }
}

export default withRouter(EventCompo);
