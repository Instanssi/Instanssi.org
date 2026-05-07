import React from 'react';
import { observer } from 'mobx-react';
import { action, runInAction, observable, computed } from 'mobx';
import { Redirect } from 'react-router';
import { Helmet } from 'react-helmet';
import { Link } from 'react-router-dom';

import globalState from 'src/state';
import { Form, FormGroup, L } from 'src/common';
import { ICompo } from 'src/api/interfaces';
import { FormStore } from 'src/stores';
import EventInfo from 'src/state/EventInfo';
import { toast } from 'react-toastify';

@observer
export default class CompoEntryAdd extends React.Component<{
    eventInfo: EventInfo;
    compo: ICompo;
}> {
    form = new FormStore({
        name: '',
        creator: '',
        description: '',
        platform: '',
        entryfile: null as File | null,
        imagefile_original: null as File | null,
        sourcefile: null as File | null,
    }, (formStore) => {
        return globalState.api.userCompoEntries.create({
            ...formStore.toJS(),
            compo: this.props.compo.id,
        });
    });

    @observable success = false;

    @action.bound
    handleSubmit(event) {
        this.form.submit().then(
            (success) => runInAction(() => {
                this.props.eventInfo.myEntries.refresh();
                this.success = true;
                toast.success(<L text="entry.addOk" values={this.form.toJS()} />);
            }),
            (_error) => runInAction(() => {
                toast.error(<L text="entry.addFail" values={this.form.toJS()} />);
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

        const returnUrl = this.props.eventInfo.getCompoURL(this.props.compo);

        if (this.success) {
            return <Redirect to={returnUrl} />;
        }

        return (
            <Form form={form} onSubmit={this.handleSubmit} leavePrompt>
                <Helmet>
                    {/* This page might not be available later. */}
                    <meta name="googlebot" content="noindex" />
                </Helmet>
                <h2><L text="entry.add" /></h2>
                <FormGroup
                    label={<L text="data.entry.name.title" />}
                    help={<L text="data.entry.name.help" />}
                    name="name"
                    required
                />
                <FormGroup
                    label={<L text="data.entry.description.title" />}
                    help={<L text="data.entry.description.help" />}
                    name="description"
                    input="textarea"
                    rows={5}
                    required
                />
                <FormGroup
                    label={<L text="data.entry.creator.title" />}
                    help={<L text="data.entry.creator.help" />}
                    name="creator"
                    required
                />
                <FormGroup
                    label={<L text="data.entry.platform.title" />}
                    help={<L text="data.entry.platform.help" />}
                    name="platform"
                />
                <FormGroup
                    label={<L text="data.entry.entryfile.title" />}
                    help={<L text="data.entry.entryfile.help" values={helpValues} />}
                    name="entryfile"
                    type="file"
                    fileMaxSize={compo.max_entry_size}
                    showClearButton
                    required
                />
                <FormGroup
                    label={<L text="data.entry.sourcefile.title" />}
                    help={<L text="data.entry.sourcefile.help" values={helpValues} />}
                    name="sourcefile"
                    type="file"
                    fileMaxSize={compo.max_source_size}
                    showClearButton
                />
                {compo.is_imagefile_allowed && <FormGroup
                    label={<L text="data.entry.imagefile_original.title" />}
                    help={<L
                        text="data.entry.imagefile_original.help"
                        values={helpValues}
                    />}
                    name="imagefile_original"
                    type="file"
                    fileMaxSize={compo.max_image_size}
                    showClearButton
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
