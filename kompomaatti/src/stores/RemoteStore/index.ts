import { observable, action, runInAction } from 'mobx';

import { IRemote } from '../interfaces';


/**
 * Holds the state of some remote value that can be fetched asynchronously
 * (with a possibility of failure).
 */
export default class RemoteStore<T, E = any> implements IRemote<T, E> {
    @observable.ref value: T | null;
    @observable.ref error: E | null;
    @observable.ref isPending = false;
    @observable.ref lastRefresh: Date | null = null;

    constructor(protected fetch: () => Promise<T>) { }

    @action
    refresh() {
        this.isPending = true;
        return this.fetch().then(
            (result) => runInAction(() => {
                this.isPending = false;
                this.value = result;
                this.error = null;
                this.lastRefresh = new Date();
                return result;
            }),
            (error) => runInAction(() => {
                this.isPending = false;
                this.error = error;
                throw error;
            }),
        );
    }
}
