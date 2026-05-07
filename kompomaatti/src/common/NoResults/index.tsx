import React from 'react';

import L from '../L';

export const NoResults = () => (
    <div className="no-results">
        <span className="fa fa-fw fa-info-circle" />
        {' '}
        {L.getText('list.noResults')}
    </div>
);
