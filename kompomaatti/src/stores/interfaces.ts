
/** The status of anything involving remote interaction. */
export interface IRemote<T, E = any> {
    /** Last successful result, if any. */
    value: T | null;
    /** Last error, if any. Cleared on successful refresh. */
    error: E | null;
    /** Is this being sync'd right now? */
    isPending: boolean;
    /** Time this was last (successfully) refreshed. */
    lastRefresh: Date | null;
    /** (Re)-fetch the value. Sets value and clears error on success. */
    refresh(): Promise<T>;
}
