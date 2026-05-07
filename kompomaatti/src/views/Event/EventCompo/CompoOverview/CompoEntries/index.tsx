import React from 'react';
import { observer } from 'mobx-react';
import { autorun, computed } from 'mobx';
import { Link, withRouter, RouteComponentProps } from 'react-router-dom';
import _orderBy from 'lodash/orderBy';
import classNames from 'classnames';

import { ICompo } from 'src/api/interfaces';
import { LoadingWrapper, NoResults, FormatNumber } from 'src/common';
import globalState from 'src/state';
import { RemoteStore } from 'src/stores';


@observer
export class CompoEntries extends React.Component<RouteComponentProps<any> & {
    compo: ICompo;
}> {
    entries = new RemoteStore(() => {
        return globalState.api.compoEntries.list({ compo: this.compoId });
    });

    disposers = [] as any[];

    componentDidMount() {
        this.disposers.push(autorun(() => {
            this.entries.refresh();
        }));
    }

    componentWillUnmount() {
        this.disposers.forEach(d => d());
    }

    get compoId() {
        const { compo } = this.props;
        return compo && compo.id;
    }

    @computed
    get allEntriesSorted() {
        return _orderBy(this.entries.value || [], entry => entry.rank);
    }

    @computed
    get qualifiedEntriesSorted() {
        return this.allEntriesSorted.filter(entry => !entry.disqualified);
    }

    getEntryPath(entry) {
        const { match } = this.props;
        return match.url + `/entries/${entry.id}`;
    }

    render() {
        const entries = this.allEntriesSorted;
        return (
            <LoadingWrapper store={this.entries}>
                {(entries && entries.length > 0) ? <ul className="list-k">
                    {entries.map(entry => (
                        <li
                            key={entry.id}
                            className={classNames(
                                'entry-item',
                                { disqualified: entry.disqualified },
                            )}
                        >
                            <span className="item-rank">
                                {entry.rank ? entry.rank + '. ' : ''}
                            </span>
                            <span className="item-score">
                                {entry.score ? <>
                                    <FormatNumber
                                        value={entry.score}
                                        precision={1}
                                    />{' p '}
                                </> : ''}
                            </span>
                            <span className="item-title">
                                <Link to={this.getEntryPath(entry)}>
                                    {entry.name}
                                </Link>&nbsp;by&nbsp;{entry.creator}
                            </span>
                        </li>
                    ))}
                </ul> : <NoResults />}
            </LoadingWrapper>
        );
    }
}

export default withRouter(CompoEntries);
