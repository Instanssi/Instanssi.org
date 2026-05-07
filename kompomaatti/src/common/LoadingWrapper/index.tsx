import React from 'react';
import { observer } from 'mobx-react';
import { action } from 'mobx';
import classNames from 'classnames';
import { IRemote } from 'src/stores';

import './loading-wrapper.scss';
import { L } from 'src/common';


@observer
export default class LoadingWrapper extends React.Component<{
    store: IRemote<any>;
    children?: any;
    className?: string | null;
}> {
    @action.bound
    handleRetry(event) {
        event.preventDefault();
        this.props.store.refresh();
    }

    render() {
        const { store, children, className } = this.props;

        return (
            <div
                className={classNames(
                    'loading-wrapper',
                    { 'is-pending': store.isPending },
                    className,
                )}
            >
                {(store.isPending && !store.value) && (
                    <div className="alert" test-id="loading">
                        <span className="fa fa-fw fa-spin fa-spinner"/>&ensp;
                        <L text="common.loading" />
                    </div>
                )}
                {(store.error && !store.isPending) && (
                    <div className="alert alert-warning">
                        <span className="fa fa-fw fa-exclamation-triangle" />&ensp;
                        <L text="common.loadingError" />
                        {' '}
                        <a
                            href="."
                            onClick={this.handleRetry}
                        >
                            <L text="common.loadingRetry" />
                        </a>
                    </div>
                )}
                {children}
            </div>
        );
    }
}
