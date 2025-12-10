import { vi, expect, test, describe, beforeEach } from 'vitest';

// Load the runtime-included build when Vue is imported
vi.mock('vue', () => import('vue/dist/vue.js'));

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
