import React from 'react';
import { observer } from 'mobx-react';
import { action } from 'mobx';

import globalState from 'src/state';
import EventInfo from 'src/state/EventInfo';
import { FormStore } from 'src/stores';
import { L, Form, FormGroup } from 'src/common';


@observer
export default class RequestCodeForm extends React.Component<{
    event: EventInfo;
    onSubmit?: (response: any) => void;
    onCancel?: () => void;
}> {
    store = new FormStore({
        text: '',
    }, (formStore) => {
        return globalState.api.voteCodeRequests.create({
            ...formStore.toJS(),
            event: this.props.event.eventId,
        });
    });

    @action.bound
    submit() {
        this.store.submit().then((response) => {
            this.props.event.myCodeRequests.refresh();
            const { onSubmit } = this.props;
            if (onSubmit) {
                onSubmit(response);
            }
        });
    }

    @action.bound
    cancel() {
        const { onCancel } = this.props;
        if (onCancel) {
            onCancel();
        }
    }

    render() {
        return (
            <Form onSubmit={this.submit} form={this.store}>
                <h4><L text="voteCode.noTicketCode" /></h4>
                <FormGroup
                    input="textarea"
                    placeholder={globalState.translate('voteCode.requestTextPlaceholder')}
                    name="text"
                />
                <button className="btn btn-primary">
                    <L text="common.submit" />
                </button>
                <button type="button" className="btn btn-link" onClick={this.cancel}>
                    <L text="common.cancel" />
                </button>
            </Form>
        );
    }
}
