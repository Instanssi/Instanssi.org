/* generated using openapi-typescript-codegen -- do not edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { Permission } from "./Permission";

export type UserInfo = {
    readonly id: number;
    /**
     * Vaaditaan. Enintään 150 merkkiä. Vain kirjaimet, numerot ja @/./+/-/_ ovat sallittuja.
     */
    username: string;
    first_name?: string;
    last_name?: string;
    email?: string;
    readonly user_permissions: Array<Permission>;
    /**
     * Antaa käyttäjälle kaikki oikeudet ilman, että niitä täytyy erikseen luetella.
     */
    readonly is_superuser: boolean;
    readonly date_joined: string;
};
