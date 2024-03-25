/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type UserData = {
    readonly id: number;
    first_name?: string;
    last_name?: string;
    email?: string;
    /**
     * Tämän käyttäjän spesifit oikeudet.
     */
    user_permissions?: Array<number>;
    /**
     * Antaa käyttäjälle kaikki oikeudet ilman, että niitä täytyy erikseen luetella.
     */
    is_superuser?: boolean;
};
