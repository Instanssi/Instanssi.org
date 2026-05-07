import React from 'react';
import { action } from 'mobx';
import { observer } from 'mobx-react';

import { L } from 'src/common';

import './fileinput.scss';

/**
 * Input for messing with files in forms.
 *
 * @todo Add option to limit acceptable file types.
 *       Mobiles may be able to offer appropriate file selectors based on them.
 * @todo Can something be done about the hideous stock file inputs?
 */
@observer
export default class FormFileInput extends React.Component<{
    value: File | undefined | null,
    /** File implies new file, undefined = keep, null = delete. */
    onChange: (newValue: File | undefined | null) => void;
    /** If there is a file currently selected, the API may provide an URL for it. */
    currentFileURL: string;
    clearable?: boolean;
}> {
    @action.bound
    handleClear() {
        this.props.onChange(null);
    }

    @action.bound
    handleChange(event) {
        // Can we preview new files?
        this.props.onChange(event.target.files && event.target.files[0] || undefined);
    }

    @action.bound
    handleKeep() {
        this.props.onChange(undefined);
    }

    @action.bound
    handleDelete() {
        this.props.onChange(null);
    }

    render() {
        const { currentFileURL } = this.props;

        return (
            <div className="form-file-input">
                <div className="file-input-current">
                    <L text="fileInput.keep" />
                    {' '}
                    {typeof currentFileURL === 'string'
                        ? <a href={currentFileURL} target="_blank">
                            <span className="fa fa-external-link" />&ensp;
                            {currentFileURL}
                        </a>
                        : (<span>
                            <span className="fa fa-times" />&ensp;
                            <L text="fileInput.noFile" />
                        </span>)
                    }
                </div>
                <div className="file-input-entry">
                    <L text="fileInput.replace" />
                    <input
                        type="file"
                        onChange={this.handleChange}
                    />
                </div>
                {/* Deleting file attachments with PATCH doesn't seem to work.
                    Maybe the users can live without this.
                <div className="file-input-delete">
                    <button
                        type="button"
                        className="btn btn-danger"
                        onClick={this.handleDelete}
                    >
                        <span className="fa fa-trash" />&ensp;
                        <L text="fileInput.delete" />
                    </button>
                </div>*/}
            </div>
        );
    }
}
