import { action, observable, toJS, runInAction } from 'mobx';
import _cloneDeep from 'lodash/cloneDeep';


export default class FormStore<T extends {}> {
    @observable value: T;
    @observable.ref error: any = null;
    @observable isPending = false;
    /** Tracks dirty state, for "leave without saving?" prompts and so on. */
    @observable isDirty = false;

    constructor(
        protected initialValue: T,
        protected submitHandler: (formStore: FormStore<T>) => Promise<any>,
    ) {
        this.value = _cloneDeep(initialValue);
    }

    /**
     * Try to send the form using the provided submit handler.
     *
     * Tracks pending state and assigns or clears error depending on the result.
     * Returns a promise, which resolves or rejects to a success or error response.
     */
    @action
    submit() {
        if (this.isPending) {
            // The UI should try to disable "submit" actions, etc. when this is pending,
            // but let's just make sure.
            return Promise.reject(null);
        }
        this.isPending = true;
        return this.submitHandler(this).then(
            (response) => runInAction(() => {
                this.isPending = false;
                this.error = null;
                this.isDirty = false;
                return response;
            }),
            (error) => runInAction(() => {
                this.isPending = false;
                this.error = error;
                throw error;
            }),
        );
    }

    @action
    reset() {
        this.value = _cloneDeep(this.initialValue);
        this.isDirty = false;
    }

    @action
    onChange(name, value) {
        if (!this.value.hasOwnProperty(name)) {
            throw new Error('Attempted to add new field to a form?');
        }
        this.value[name] = value;
        this.isDirty = true;
    }

    @action
    setValue(value) {
        // TODO: Validate that the field names sort of match?
        this.value = value;
        this.isDirty = false;
    }

    @action
    setError(error) {
        this.error = error;
    }

    /**
     * Return a copy of the value as a JSON string.
     *
     * Don't expect this to work if the data isn't compatible with plain JSON.
     */
    toJSON() {
        return JSON.stringify(this.value);
    }

    /**
     * Return a copy of the value as a plain JS object.
     */
    toJS() {
        return toJS(this.value);
    }
}
