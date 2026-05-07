import React from 'react';
import { observer } from 'mobx-react';

import { apiState } from 'src/api/BaseAPI';

import './cube.scss';

export class Cube extends React.Component<{
    active?: boolean;
}> {
    render() {
        const { active } = this.props;
        const className = active ? 'cube-wrap active' : 'cube-wrap';
        return (
            <div className={className}>
                <div className="cube">
                    <div className="side-top" />
                    <div className="side-bottom" />
                    <div className="side-left" />
                    <div className="side-right" />
                    <div className="side-front" />
                    <div className="side-back" />
                </div>
                <div className="cube-glare" />
            </div>
        );
    }
}

/**
 * Animates the cube based on ongoing API requests.
 */
@observer
export class ActivityCube extends React.Component {
    render() {
        const { requests } = apiState;
        return <Cube active={requests > 0} />;
    }
}
