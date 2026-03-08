import { vi, expect, test, describe, beforeEach } from 'vitest';

vi.mock('./store_api', () => ({
    storeXHR: (method: string, path: string, data: unknown) => {
        return Promise.resolve([]);
    },
}));

describe('Instanssi Store', () => {
    /** @type {HTMLElement} */
    let element;

    beforeEach(() => {
        element = document.createElement('div');
        element.id = 'store';
        document.body.appendChild(element);
    });
    
    test('initializes', async () => {
        await import('./index.js');
        const store = element.firstChild;
        expect(store).toBeDefined();
    });
});
