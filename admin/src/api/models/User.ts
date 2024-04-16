/* generated using openapi-typescript-codegen -- do not edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { Group } from "./Group";
import type { Permission } from "./Permission";

export type User = {
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
    readonly groups: Array<Group>;
    /**
     * Määrää, voiko käyttäjä kirjautua sisään. Tällä voi estää käyttäjätilin käytön poistamatta sitä.
     */
    is_active?: boolean;
};
