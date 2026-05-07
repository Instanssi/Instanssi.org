import React from 'react';
import { observer } from 'mobx-react';
import { computed } from 'mobx';

import { ICompoEntry } from 'src/api/interfaces';
import { L } from 'src/common';
import { isImageURL, isAudioURL } from 'src/utils';

interface IImageURLs {
    medium: string;
    original: string;
}

/**
 * Common code for displaying a compo entry's details.
 */
@observer
export default class EntryInfo extends React.Component<{
    entry: ICompoEntry;
}> {

    @computed
    get entryImageURLs(): IImageURLs | null {
        const { entryfile_url } = this.props.entry;
        if (entryfile_url && isImageURL(entryfile_url)) {
            return {
                medium: entryfile_url,
                original: entryfile_url,
            };
        }
        return null;
    }

    @computed
    get isAudioEntry(): boolean {
        const { entryfile_url } = this.props.entry;
        return !!entryfile_url && isAudioURL(entryfile_url);
    }

    render() {
        const { entry } = this.props;
        const { entryImageURLs } = this;
        const { isAudioEntry } = this;
        return (
            <>
                <div className="entry-title">
                    <h3>{entry.name}</h3>
                    <p>by {entry.creator}</p>
                </div>
                {!!entry.youtube_url && <div className="entry-video">
                    <h4><L text="entry.video" /></h4>
                    <p>
                        <a target="_blank" href={entry.youtube_url}>
                            <span className="fa fa-fw fa-youtube" />&ensp;
                            <L text="entry.youtubeLink" />
                        </a>
                    </p>
                </div>}
                {isAudioEntry && entry.entryfile_url && (
                    <div className="entry-audio">
                        <h4><L text="entry.audio" /></h4>
                        <audio src={entry.entryfile_url} autoPlay={false} controls />
                        <p><L text="entry.audioHelp" /></p>
                    </div>
                )}
                {entry.imagefile_medium_url && (
                    <div className="entry-image">
                        <h4><L text="entry.image" /></h4>
                            <a target="_blank" href={entry.imagefile_original_url || ''}>
                                <img src={entry.imagefile_medium_url} />
                            </a>
                    </div>
                )}
                {(!entry.imagefile_medium_url && entryImageURLs) && (
                    <div className="entry-image">
                        <h4><L text="entry.image" /></h4>
                            <a target="_blank" href={entryImageURLs.original || ''}>
                                <img src={entryImageURLs.medium} />
                            </a>
                    </div>
                )}
                {entry.disqualified && <div className="entry-disqualified">
                    <h4><L text="data.entry.disqualified.title" /></h4>
                    <p>{entry.disqualified_reason}</p>
                </div>}
                {entry.platform && (
                    <>
                        <h4><L text="data.entry.platform.title" /></h4>
                        <p>{entry.platform}</p>
                    </>
                )}
                <div className="entry-description">
                    <h4><L text="entry.description" /></h4>
                    <p className="text-pre-wrap">{entry.description}</p>
                </div>
                <div className="entry-files">
                    <h4><L text="entry.files" /></h4>
                    {entry.entryfile_url && <p>
                        <a target="_blank" href={entry.entryfile_url}>
                            <span className="fa fa-fw fa-download" />&ensp;
                            <L text="entry.entryfile" />
                        </a>
                    </p>}
                    {entry.sourcefile_url && <p>
                        <a target="_blank" href={entry.sourcefile_url}>
                            <span className="fa fa-fw fa-download" />&ensp;
                            <L text="entry.sourcefile" />
                        </a>
                    </p>}
                </div>
            </>
        );
    }
}
