/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PatchedCompoEntryRequest = {
    /**
     * Kompo johon osallistutaan
     */
    compo?: number;
    /**
     * Nimi tuotokselle
     */
    name?: string;
    /**
     * Voi sisältää mm. tietoja käytetyistä tekniikoista, muuta sanottavaa.
     */
    description?: string;
    /**
     * Tuotoksen tekijän tai tekijäryhmän nimi
     */
    creator?: string;
    /**
     * Alusta jolla entry toimii. Voit jättää tyhjäksi jos entry ei sisällä ajettavaa koodia.
     */
    platform?: string | null;
};
