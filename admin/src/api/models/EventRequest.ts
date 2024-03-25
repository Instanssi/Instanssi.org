/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type EventRequest = {
    /**
     * Tapahtuman nimi
     */
    name: string;
    /**
     * Tapahtuman päivämäärä (alku)
     */
    date: string;
    /**
     * Saa näyttää arkistossa
     */
    archived?: boolean;
    /**
     * URL Tapahtuman pääsivustolle
     */
    mainurl?: string;
};
