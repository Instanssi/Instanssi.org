import React from 'react';
import {  act, RenderResult, waitFor } from '@testing-library/react';
import { describe, beforeEach, it, expect } from 'vitest';
import { mockCompoEntry, mockCompo } from 'src/tests/mocks';
import globalState from 'src/state';
import { CompoEntry } from './';
import { testRender } from 'src/tests';


describe(CompoEntry.name, () => {
    let rendered: RenderResult;
    let mockProps;

    beforeEach(async () => {
        mockProps = {
            eventInfo: {
                event: {},
            },
            compo: mockCompo,
            match: {
                params: {
                    entryId: '' + mockCompoEntry.id,
                },
            },
        };
        // Render the view and wait for it to stop loading things
        await act(async () => {
            rendered = testRender(<CompoEntry {...mockProps} />);
            await waitFor(() => !rendered.queryByTestId('loading'))
        });
    });

    it('renders after fetching the entry', async () => {
        await waitFor(() => rendered.findByText(mockCompoEntry.name));
    });

    it('calls the API to fetch entry details', async () => {
        await waitFor(() => rendered.findByText(mockCompoEntry.name));
        expect(globalState.api.compoEntries.get)
            .toHaveBeenCalledWith(mockCompoEntry.id);
    });
});
