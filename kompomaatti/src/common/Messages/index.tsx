import React from 'react';
import { observable, action } from 'mobx';
import { observer } from 'mobx-react';
import globalState from 'src/state';
import L from '../L';

import './messages.scss';

@observer
export class Messages extends React.Component {
    @observable hovered = false;

    timeout: any = null;

    componentWillUnmount() {
        this.stopTimer();
    }

    @action.bound
    handleMouseMove() {
        this.stopTimer();
        this.hovered = true;
        this.timeout = setTimeout(action(() => {
            this.hovered = false;
        }), 2000);
    }

    stopTimer() {
        if (this.timeout !== null) {
            clearTimeout(this.timeout);
            this.timeout = null;
        }
    }

    get messages() {
        return globalState.messages;
    }

    render() {
        const { messages, hovered } = this;
        const className = hovered ? 'messages hovered' : 'messages';

        return (
            <ul className={className} onMouseMove={this.handleMouseMove}>
                {messages.map(msg => (
                    <div
                        key={msg.id}
                        className={`message alert alert-${msg.type || 'info'}`}
                    >
                        <L text={msg.text} values={msg.values} />
                    </div>
                ))}
            </ul>
        );
    }
}
