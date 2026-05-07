import React from 'react';
import { it, vi, describe, beforeEach, expect } from 'vitest';

import globalState from 'src/state';

import { EventView } from './';
import { RenderResult } from '@testing-library/react';
import { testRender } from 'src/tests';
// import EventInfo from 'src/state/EventInfo';

vi.mock('src/state', async () => {
    const { mockEvent } = await import ('src/tests');
    const einfo = (await import('src/state/EventInfo')).default;
    return {
        default: {
            events: {
                value: [
                    { eventId: mockEvent.id + 1 } as any,
                    new einfo(null as any, mockEvent),
                    { eventId: mockEvent.id + 2 } as any,
                ],
            },
        }
    };
});

describe(EventView.name, () => {
    let wrapper: RenderResult;
    // let instance;
    let mockProps;

    beforeEach(() => {
        const eventId = globalState.events.value![1].eventId;
        mockProps = {
            match: {
                params: {
                    eventId: String(eventId),
                },
            },
            location: {
                pathname: `/events/${eventId}`,
            }
        };

        wrapper = testRender(<EventView {...mockProps} />);
        // instance = wrapper.instance();
    });

    it('renders', () => {
        expect(wrapper.baseElement.querySelector('.event-view')).toBeDefined();
    });
});
