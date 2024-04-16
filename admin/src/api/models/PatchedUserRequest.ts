/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PatchedUserRequest = {
    /**
     * Vaaditaan. Enintään 150 merkkiä. Vain kirjaimet, numerot ja @/./+/-/_ ovat sallittuja.
     */
    username?: string;
    first_name?: string;
    last_name?: string;
    email?: string;
    /**
     * Määrää, voiko käyttäjä kirjautua sisään. Tällä voi estää käyttäjätilin käytön poistamatta sitä.
     */
    is_active?: boolean;
};
