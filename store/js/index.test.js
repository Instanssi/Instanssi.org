import Vue from 'vue';

jest.mock('./store_api', () => ({
    storeXHR: jest.fn((method, path, data) => {
        return Promise.resolve([]);
    }),
}));

describe('Instanssi Store', () => {
    /** @type {HTMLElement} */
    let element;

    beforeEach(() => {
        element = document.createElement('div');
        element.id = 'store';
        document.body.appendChild(element);

        require('./');
    });

    it('initializes', () => {
        const store = element.firstChild;
        expect(store).toBeDefined();
    });
});
