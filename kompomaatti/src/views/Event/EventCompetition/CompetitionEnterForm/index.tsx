import React from 'react';
import { observer } from 'mobx-react';
import { action, runInAction } from 'mobx';

import globalState from 'src/state';
import { Form, FormGroup, L } from 'src/common';
import { ICompetition } from 'src/api/interfaces';
import { FormStore } from 'src/stores';
import EventInfo from 'src/state/EventInfo';

@observer
export default class CompetitionEnterForm extends React.Component<{
    eventInfo: EventInfo;
    competition: ICompetition;
    onSubmit: (response: any) => void;
    onCancel: () => void;
}> {
    form = new FormStore({
        participant_name: '',
    }, (formStore) => {
        return globalState.api.userCompetitionParticipations.create({
            ...formStore.toJS(),
            competition: this.props.competition.id,
        });
    });

    @action.bound
    handleSubmit(event) {
        this.form.submit().then(
            (success) => runInAction(() => {
                this.props.eventInfo.myParticipations.refresh();
                this.props.onSubmit(success);
            }),
            (error) => runInAction(() => {
                this.form.setError(error);
            }),
        );
    }

    render() {
        const { form } = this;
        return (
            <Form form={form} onSubmit={this.handleSubmit} leavePrompt>
                <h3><L text="competition.participate" /></h3>
                <FormGroup
                    label={<L text="data.c22n.participant_name.title" />}
                    help={<L text="data.c22n.participant_name.help" />}
                    name="participant_name"
                />
                <div>
                    <button className="btn btn-primary" disabled={this.form.isPending}>
                        <L text="common.submit" />
                    </button>
                    &ensp;
                    <button
                        type="button"
                        className="btn btn-link"
                        disabled={this.form.isPending}
                        onClick={this.props.onCancel}
                    >
                        <L text="common.cancel" />
                    </button>
                </div>
            </Form>
        );
    }
}

