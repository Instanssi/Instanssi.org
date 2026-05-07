import React from 'react';
import { observer } from 'mobx-react';
import Modal from 'react-bootstrap/lib/Modal';

import { ICompoEntry } from 'src/api/interfaces';
import { L } from 'src/common';

import EntryInfo from '../EntryInfo';

/**
 * Displays entry information in a modal.
 */
@observer
export default class EntryModal extends React.Component<{
    entry: ICompoEntry;
    onClose: () => any;
}> {
    render() {
        const { entry, onClose } = this.props;
        return (
            <Modal show onHide={onClose} className="compo-entry-modal">
                <Modal.Header closeButton>
                    <Modal.Title>
                        <L text="entry.info" />
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <EntryInfo entry={entry} />
                </Modal.Body>
                <Modal.Footer>
                    <button
                        type="button"
                        className="btn btn-primary"
                        onClick={onClose}
                    >
                        <L text="common.back" />
                    </button>
                </Modal.Footer>
            </Modal>
        );
    }
}
