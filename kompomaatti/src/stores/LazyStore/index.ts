import { createAtom, runInAction } from 'mobx';

import { IRemote } from 'src/stores';

export interface IStoreOptions {
    /**
     * Delay before the data is considered outdated and will be re-fetched on the next access,
     * in milliseconds. 0 or undefined = no auto refresh.
     */
    refreshInterval?: number;
}

/**
 * Like a RemoteStore, but only fetches its value once something looks at it.
 *
 * Can be used to declare some remote data without actually fetching it immediately.
 */
export default class LazyStore<T, E = any> implements IRemote<T, E> {
    protected _value: T | null;
    protected _error: E | null;
    protected _currentFetch: Promise<T> | null = null;
    protected _lastRefresh: Date | null = null;
    protected _observed = 0;

    /**
     * Tracks observation.
     *
     * Call atom.reportObserved() when observable data is accessed,
     * and atom.reportChanged() then the data changes.
     */
    protected atom = createAtom(
        'AtomStore',
        () => this.onObserved(),
        () => this.onUnobserved(),
    );

    constructor(protected fetch: () => Promise<T>, protected options: IStoreOptions = {}) { }

    get value() {
        this.handleAccess();
        return this._value;
    }

    get error() {
        this.handleAccess();
        return this._error;
    }

    get isPending() {
        this.handleAccess();
        return this._currentFetch !== null;
    }

    get lastRefresh() {
        this.handleAccess();
        return this._lastRefresh;
    }

    clear() {
        this._value = null;
        this.atom.reportChanged();
    }

    refresh() {
        if (this._currentFetch) {
            return this._currentFetch;
        }
        const promise = this.fetch().then(
            (result) => runInAction(() => {
                this._value = result;
                this._error = null;
                this._lastRefresh = new Date();
                this._currentFetch = null;
                this.atom.reportChanged();
                return result;
            }),
            (error) => runInAction(() => {
                this._error = error;
                this._currentFetch = null;
                this.atom.reportChanged();
                throw error;
            }),
        );
        this._currentFetch = promise;
        this.atom.reportChanged();
        return promise;
    }

    protected handleAccess() {
        if (this.atom.reportObserved()) {
            return;
        } else {
            // Called from outside an observer/reaction; cycle anyway just this once.
            console.warn('Data accessed outside observer context?', this);
            this.maybeRefresh();
        }
    }

    protected maybeRefresh() {
        const { _lastRefresh, _currentFetch } = this;
        const { refreshInterval } = this.options;

        const neverFetched = !_currentFetch && !_lastRefresh;

        const now = new Date().getTime();
        const outdated = (refreshInterval && _lastRefresh)
            && (now - _lastRefresh.getTime()) > refreshInterval;

        // console.info('maybeRefresh:', neverFetched, outdated);

        if (neverFetched || outdated) {
            this.refresh();
        }
    }

    protected onObserved() {
        this._observed++;
        this.maybeRefresh();
    }

    protected onUnobserved() {
        // TODO: Use something smarter than promises so we can cancel fetches?
        // console.info('AtomStore unobserved.');
        this._observed--;
    }
}
