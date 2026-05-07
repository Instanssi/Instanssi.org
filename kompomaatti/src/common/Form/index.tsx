import React from 'react';
import { observer, Provider } from 'mobx-react';
import { action, computed } from 'mobx';
import { Prompt, withRouter } from 'react-router';

import { FormStore } from 'src/stores';
import FormFeedback from '../FormFeedback';
import { L } from '..';

@(withRouter as any)
@observer
export default class Form<T> extends React.Component<{
    /** Form state to connect to. */
    form: FormStore<T>;
    /**
     * Called when the form's submit event fires.
     *
     * The default action is prevented before this.
     */
    onSubmit: (value: FormStore<T>) => void;
    /** Arbitrary content. */
    children?: any;
    /** Prompt user when leaving the page? */
    leavePrompt?: boolean | string;
}> {
    @action.bound
    handleSubmit(event) {
        event.preventDefault();
        const { props } = this;
        props.onSubmit(props.form);
    }

    @computed
    get leavePromptText() {
        const { leavePrompt } = this.props;
        if (typeof leavePrompt === 'string') {
            return leavePrompt;
        }
        return L.getText('common.leaveWithoutSaving');
    }

    render() {
        const { props } = this;
        return (
            <Provider formStore={props.form}>
                <form onSubmit={this.handleSubmit}>
                    {!!props.leavePrompt && (
                        <Prompt
                            when={props.form.isDirty}
                            message={this.leavePromptText}
                        />
                    )}
                    {props.children}
                    <FormFeedback form={props.form} />
                    <FormFeedback form={props.form} name="non_field_errors" />
                </form>
            </Provider>
        );
    }
}
