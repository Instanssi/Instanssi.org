/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type BlogEntry = {
    readonly id: number;
    user?: number;
    readonly date: string;
    /**
     * Lyhyt otsikko entrylle.
     */
    title: string;
    text: string;
    /**
     * Mikäli entry on julkinen, tulee se näkyviin sekä tapahtuman sivuille että RSS-syötteeseen.
     */
    public?: boolean;
    event: number;
};
