import { vi } from 'vitest';
import type { PrimaryKey } from '../../src/api/interfaces';
import { mockCompetition, mockCompo, mockCompoEntry, mockEvent, mockUser } from '../../src/tests/mocks';


vi.mock("../../src/api", () => {
    // Mock enough of the API to let the global stuff work
    return {
        api: {
            currentUser: {
                get: vi.fn(() => Promise.resolve(mockUser)),
            },
            events: {
                list: vi.fn(() => Promise.resolve([mockEvent])),
            },
            compos: {
                list: vi.fn(() => Promise.resolve([mockCompo])),
            },
            compoEntries: {
                get: vi.fn((_id: PrimaryKey) => Promise.resolve(mockCompoEntry)),
            },
            voteCodes: {
                list: vi.fn(() => Promise.resolve([]))
            },
            voteCodeRequests: {
                list: vi.fn(() => Promise.resolve([]))
            },
            competitions: {
                list: vi.fn(() => Promise.resolve([mockCompetition]))
            },
            programme: {
                list: vi.fn(() => Promise.resolve([])),
            }
        }
    }
});
