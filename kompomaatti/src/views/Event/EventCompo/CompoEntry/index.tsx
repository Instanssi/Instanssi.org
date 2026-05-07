import React from 'react';
import { observer } from 'mobx-react';
import { autorun } from 'mobx';
import { withRouter, RouteComponentProps } from 'react-router';
import { Helmet } from 'react-helmet';

import globalState from 'src/state';
import { ICompo } from 'src/api/interfaces';
import { RemoteStore } from 'src/stores';
import { L, LoadingWrapper } from 'src/common';
import EventInfo from 'src/state/EventInfo';
import EntryInfo from '../EntryInfo';

@observer
export class CompoEntry extends React.Component<{
    eventInfo: EventInfo;
    compo: ICompo;
} & RouteComponentProps<{ entryId: string }>> {
    entry = new RemoteStore(() => {
        return globalState.api.compoEntries.get(this.entryId);
    });

    disposers = [] as any[];

    componentDidMount() {
        this.disposers = [
            autorun(() => this.entry.refresh()),
        ];
    }

    componentWillUnmount() {
        this.disposers.forEach(d => d());
    }

    get entryId() {
        const { params } = this.props.match;
        return Number.parseInt(params.entryId, 10);
    }

    render() {
        const { eventInfo } = this.props;
        const entry = this.entry.value;

        return (
            <LoadingWrapper className="compo-entry" store={this.entry}>
                {entry && <div className="entry-info">
                    <Helmet>
                        <title>{`${entry.name} @ ${eventInfo.event.name}`}</title>
                        <meta
                            property="og:title"
                            content={entry.name}
                        />
                        {entry.description && entry.description.length > 0 && (
                            <meta
                                name="description"
                                content={entry.description}
                            />
                        )}
                        {entry.description && entry.description.length > 0 && (
                            <meta
                                property="og:description"
                                content={entry.description}
                            />
                        )}
                        {entry.imagefile_original_url && (
                            <meta
                                property="og:image"
                                content={entry.imagefile_original_url}
                            />
                        )}
                    </Helmet>
                    <EntryInfo entry={entry} />
                </div>}
            </LoadingWrapper>
        );
    }
}

export default withRouter(CompoEntry);
