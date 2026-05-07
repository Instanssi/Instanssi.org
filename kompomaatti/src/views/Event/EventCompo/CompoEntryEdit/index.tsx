import React from 'react';
import { observer } from 'mobx-react';
import { action, runInAction, reaction, computed, observable } from 'mobx';
import { RouteComponentProps, withRouter, Redirect } from 'react-router';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';

import globalState from 'src/state';
import { Form, FormGroup, FormFileInput, L } from 'src/common';
import { ICompo, ICompoEntry } from 'src/api/interfaces';
import { FormStore } from 'src/stores';
import EventInfo from 'src/state/EventInfo';
import { toast } from 'react-toastify';


@observer
export class CompoEntryEdit extends React.Component<{
    eventInfo: EventInfo;
    compo: ICompo;
    entry: ICompoEntry;
}> {
    form = new FormStore({
        name: '',
        creator: '',
        description: '',
        platform: '',
        // This should allow "undefined" values when the file is to remain unchanged.
        // To delete the file, set this to an empty string; pass a new file to replace it.
        entryfile: null as File | null,
        imagefile_original: null as File | null,
        sourcefile: null as File | null,
    }, (formStore) => {
        return globalState.api.userCompoEntries.update(
            this.props.entry.id,
            {
                ...formStore.toJS(),
                compo: this.props.compo.id,
            },
        );
    });

    @observable success = false;

    disposers: any[] = [];

    componentDidMount() {
        this.disposers.push(reaction(
            () => this.props.entry,
            (entry) => {
                this.updateForm(entry);
            },
            { fireImmediately: true },
        ));
    }

    componentWillUnmount() {
        this.disposers.forEach(d => d());
    }


    updateForm(entry: ICompoEntry) {
        this.form.setValue({
            name: entry.name || '',
            creator: entry.creator || '',
            description: entry.description || '',
            youtube_url: entry.youtube_url || '',
            platform: entry.platform || '',
            // The file inputs should show placeholders for any existing values.
            entryfile: undefined,
            imagefile_original: undefined,
            sourcefile: undefined,
        });
    }

    @action.bound
    handleSubmit(event) {
        this.form.submit().then(
            (success) => runInAction(() => {
                console.info('success:', success);
                this.props.eventInfo.myEntries.refresh();
                this.success = true;
                toast.success(<L text="entry.editOk" values={this.form.toJS()} />);
            }),
            (_error) => runInAction(() => {
                toast.error(<L text="entry.editFail" values={this.form.toJS()} />);
            }),
        );
    }

    @computed
    get helpValues() {
        const { compo } = this.props;
        return {
            entryFormats: compo.entry_format_list.join(', '),
            entryMaxSize: Math.floor(compo.max_entry_size / 1024),
            imageFormats: compo.image_format_list.join(', '),
            imageMaxSize: Math.floor(compo.max_image_size / 1024),
            sourceFormats: compo.source_format_list.join(', '),
            sourceMaxSize: Math.floor(compo.max_source_size / 1024),
        };
    }

    render() {
        const { compo } = this.props;
        const { form, helpValues } = this;
        const { sourcefile_url, entryfile_url, imagefile_original_url } = this.props.entry;

        const returnUrl = this.props.eventInfo.getCompoURL(this.props.compo);

        if (this.success) {
            return <Redirect to={returnUrl} />;
        }

        return (
            <Form form={form} onSubmit={this.handleSubmit} leavePrompt>
                <h2><L text="entry.edit" /></h2>
                <FormGroup
                    name="name"
                    label={<L text="data.entry.name.title" />}
                    help={<L text="data.entry.name.help" />}
                    required
                />
                <FormGroup
                    name="description"
                    label={<L text="data.entry.description.title" />}
                    help={<L text="data.entry.description.help" />}
                    input="textarea"
                    lines={5}
                    required
                />
                <FormGroup
                    name="creator"
                    label={<L text="data.entry.creator.title" />}
                    help={<L text="data.entry.creator.help" />}
                    required
                />
                <FormGroup
                    label={<L text="data.entry.platform.title" />}
                    help={<L text="data.entry.platform.help" />}
                    name="platform"
                />
                <FormGroup
                    name="entryfile"
                    label={<L text="data.entry.entryfile.title" />}
                    help={<L text="data.entry.entryfile.help" values={helpValues} />}
                    input={FormFileInput}
                    currentFileURL={entryfile_url}
                    required
                />
                <FormGroup
                    name="sourcefile"
                    label={<L text="data.entry.sourcefile.title" />}
                    help={<L text="data.entry.sourcefile.help" values={helpValues} />}
                    input={FormFileInput}
                    currentFileURL={sourcefile_url}
                />
                {compo.is_imagefile_allowed && <FormGroup
                    name="imagefile_original"
                    label={<L text="data.entry.imagefile_original.title" />}
                    help={<L text="data.entry.imagefile_original.help" values={helpValues} />}
                    input={FormFileInput}
                    currentFileURL={imagefile_original_url}
                />}
                <div>
                    <button className="btn btn-primary" disabled={this.form.isPending}>
                        <span className={`fa fa-fw ${form.isPending ? 'fa-spin fa-spinner' : 'fa-check'}`} />
                        &ensp;
                        <L text="common.submit" />
                    </button>

                    <Link to={returnUrl} className="btn btn-text">
                        <L text="common.cancel" />
                    </Link>
                </div>
            </Form>
        );
    }
}

@observer
export class CompoEntryEditView extends React.Component<{
    eventInfo: EventInfo;
    compo: ICompo;
} & RouteComponentProps<{ entryId: string }>> {
    get idParsed() {
        return Number.parseInt(this.props.match.params.entryId, 10);
    }

    @computed
    get entry() {
        const { value } = this.props.eventInfo.myEntries;
        return value && value.find(entry => entry.id === this.idParsed);
    }

    get isPending() {
        return this.props.eventInfo.myEntries.isPending;
    }

    render() {
        const { eventInfo, compo } = this.props;
        const { entry } = this;
        if (entry) {
            return (
                <>
                    <Helmet>
                        {/* This page might not be available later. */}
                        <meta name="googlebot" content="noindex" />
                    </Helmet>

                    <CompoEntryEdit
                        eventInfo={eventInfo}
                        compo={compo}
                        entry={entry}
                    />
                </>
            );
        }
        if (!this.isPending) {
            return <Redirect to={eventInfo.eventURL} />;
        }
        return null;
    }
}

// TODO: Should this form be part of a larger component that does this?
export default withRouter(CompoEntryEditView);
