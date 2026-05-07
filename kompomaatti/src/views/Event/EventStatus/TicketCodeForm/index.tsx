import React from 'react';
import { observer } from 'mobx-react';
import { action } from 'mobx';

import globalState from 'src/state';
import EventInfo from 'src/state/EventInfo';
import { FormStore } from 'src/stores';
import { L, Form, FormGroup } from 'src/common';


@observer
export default class TicketCodeForm extends React.Component<{
    event: EventInfo;
    onSubmit?: (response: any) => void;
    onCancel?: () => void;
}> {
    store = new FormStore({
        ticket_key: '',
    }, (formStore) => {
        return globalState.api.voteCodes.create({
            ...formStore.toJS(),
            event: this.props.event.eventId,
        });
    });

    @action.bound
    handleSubmit() {
        this.store.submit().then((response) => {
            this.props.event.myVoteCodes.refresh();
            const { onSubmit } = this.props;
            if (onSubmit) {
                onSubmit(response);
            }
        });
    }

    @action.bound
    handleCancel() {
        const { onCancel } = this.props;
        if (onCancel) {
            onCancel();
        }
    }

    render() {
        return (
            <Form onSubmit={this.handleSubmit} form={this.store}>
                <h4><L text="voteCode.useTicketCode" /></h4>
                <FormGroup
                    name="ticket_key"
                    placeholder={globalState.translate('voteCode.ticketKeyPlaceholder')}
                />
                <button className="btn btn-primary">
                    <L text="common.submit" />
                </button>
                <button type="button" className="btn btn-link" onClick={this.handleCancel}>
                    <L text="common.cancel" />
                </button>
            </Form>
        );
    }
}
