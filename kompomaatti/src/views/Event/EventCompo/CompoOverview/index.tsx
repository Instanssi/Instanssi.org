import React from 'react';
import { observer } from 'mobx-react';
import { computed } from 'mobx';
import moment from 'moment';

import { L } from 'src/common';

import { ICompo } from 'src/api/interfaces';
import EventInfo from 'src/state/EventInfo';

import CompoEntries from './CompoEntries';
import CompoStatus from '../CompoStatus';
import globalState from 'src/state';


@observer
export default class CompoOverview extends React.Component<{
    compo: ICompo;
    eventInfo: EventInfo;
}> {

    @computed
    get descriptionHTML() {
        return {
            __html: this.props.compo.description,
        };
    }

    @computed
    get schedule() {
        const { compo } = this.props;
        const parse = v => v ? moment(v) : null;

        // Could just map the compo JSON into something with these sooner.
        return {
            addingEnd: parse(compo.adding_end),
            editingEnd: parse(compo.editing_end),
            compoStart: parse(compo.compo_start),
            votingStart: parse(compo.voting_start),
            votingEnd: parse(compo.voting_end),
        };
    }

    @computed
    get entriesArePublic() {
        return moment(this.props.compo.voting_start).isBefore(globalState.timeMin);
    }

    render() {
        const { compo, eventInfo } = this.props;
        const { entriesArePublic } = this;

        return (
            <div className="event-compo-overview">
                <CompoStatus eventInfo={eventInfo} compo={compo} />
                {entriesArePublic && (
                    <div className="compo-entries">
                        <h3><L text="compo.entries" /></h3>
                        <CompoEntries compo={compo} />
                    </div>
                )}
                <div className="compo-description">
                    <h3><L text="common.description" /></h3>
                    <div dangerouslySetInnerHTML={this.descriptionHTML} />
                </div>
            </div>
        );
    }
}
