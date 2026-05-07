import React from 'react';
import { observer, inject } from 'mobx-react';
import { action, computed } from 'mobx';
import classNames from 'classnames';
import _get from 'lodash/get';

import { FormStore } from 'src/stores';
import FormFeedback from '../FormFeedback';
import L from '../L';

export interface IFormGroupProps<T> {
    name: string;
    label?: JSX.Element | string;
    help?: JSX.Element | string;

    /**
     * Set to use a custom input component. A text input is rendered by default.
     *
     * The class is used with props that would work with a plain <input />.
     */
    input?: React.ComponentClass<any> | string;

    // Tempted to just make this interface extend basic HTML input attributes,
    // but most of that junk is useless and potentially confusing.
    type?: string;
    readOnly?: boolean;

    /**
     * Set to completely override the input field implementation.
     */
    children?: JSX.Element;

    /** Actually passed via MobX provider + inject (context). */
    formStore?: FormStore<T>;

    /** If uploading a file, this sets a max allowed size. */
    fileMaxSize?: number;
    showClearButton?: boolean;

    /** Indicate that this field is required. */
    required?: boolean;
}

/**
 * Markup for a form group.
 */
@inject('formStore')
@observer
export default class FormGroup<T> extends React.Component<
    IFormGroupProps<T> & any
> {
    inputRef: HTMLInputElement | null = null;

    componentDidMount() {
        // sanity checks
        const { name, formStore } = this.props;

        if (!formStore) {
            throw new Error('No formStore provided!');
        }

        if (!formStore.value.hasOwnProperty(name)) {
            throw new Error('Key: ' + name + ' not in form value!');
        }
    }

    /** Get id for the form label and control. */
    get id() {
        return this.props.name;
    }

    @action.bound
    onChange(eventOrValue) {
        const { name, type } = this.props;
        const form = this.props.formStore!;
        if (!eventOrValue) {
            return form.onChange(name, eventOrValue);
        }
        const { target } = eventOrValue;

        if (target) {
            // how about checkboxes? they have "checked" instead of "value" because DOM is silly
            // - do they belong in form groups anyway?
            if (type === 'file') {
                return form.onChange(name, target.files && target.files[0]);
            } else {
                return form.onChange(name, target.value);
            }
        }
        return form.onChange(name, eventOrValue);
    }

    @action.bound
    clearValue() {
        const { name, type } = this.props;
        const form = this.props.formStore!;

        if (this.inputRef && type === 'file') {
            this.inputRef.value = '';
        }

        return form.onChange(name, null);
    }

    @computed
    get value() {
        const { formStore, name } = this.props;
        return _get(formStore!.value, name);
    }

    @computed
    get errors() {
        const { name, formStore, type } = this.props;
        if (!formStore.error) {
            return null;
        }
        // Any error is expected to be a map of field names to arrays of problems.
        return formStore.error[name!] as (string[] | null);
    }

    handleRef = ref => {
        this.inputRef = ref;
    };

    render() {
        const { id, props, value, onChange } = this;
        const {
            name,
            label,
            help,
            input,
            children,
            formStore,
            type,
            fileMaxSize,
            readOnly,
            showClearButton,
            required,
            ...rest
        } = props;

        let fileSizeWarning = false;

        if (type === 'file' && fileMaxSize && value && value instanceof File) {
            if (value.size > fileMaxSize) {
                fileSizeWarning = true;
            }
        }

        const className = classNames('form-group', {
            'has-error': !!this.errors || fileSizeWarning,
        });

        // If no input field was provided, render a text input bound to
        //  the appropriate form field. This could handle like 50% of cases.

        const inputContent = children
            ? children
            : React.createElement(input || 'input', {
                  id,
                  // HTML forms, please don't suck this hard
                  value: type !== 'file' ? value : value && value.filename,
                  type,
                  onChange,
                  className: 'form-control',
                  readOnly: readOnly || formStore!.isPending,
                  ref: this.handleRef,
                  ...rest,
              });

        return (
            <div className={className}>
                {label && (
                    // Tie the label contents to the form input to ease navigation.
                    <label className="control-label" htmlFor={id}>
                        {label}
                        {required && ' *'}
                    </label>
                )}
                {showClearButton ? (
                    <div className="input-group">
                        {inputContent}
                        <span className="input-group-btn">
                            <button
                                type="button"
                                className="btn btn-default"
                                disabled={!value}
                                onClick={this.clearValue}
                            >
                                <span className="fa fa-fw fa-trash" />
                            </button>
                        </span>
                    </div>
                ) : (
                    inputContent
                )}
                {help && (
                    // Render help text using Bootstrap 3 markup.
                    <p className="help-block">{help}</p>
                )}
                {fileMaxSize && fileSizeWarning && (
                    <div className="alert alert-warning">
                        <L
                            text="common.fileMaxSize"
                            values={{
                                // FIXME: Localize number properly
                                // - may need some refactoring in FormatNumber
                                size: (fileMaxSize / (1024 * 1024)).toFixed(1),
                                unit: 'MiB',
                            }}
                        />
                    </div>
                )}
                <FormFeedback form={formStore!} name={name} />
            </div>
        );
    }
}
