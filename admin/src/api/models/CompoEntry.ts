/* generated using openapi-typescript-codegen -- do not edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { AlternateEntryFile } from "./AlternateEntryFile";

export type CompoEntry = {
    readonly id: number;
    /**
     * Kompo johon osallistutaan
     */
    compo: number;
    /**
     * Nimi tuotokselle
     */
    name: string;
    /**
     * Voi sisältää mm. tietoja käytetyistä tekniikoista, muuta sanottavaa.
     */
    description: string;
    /**
     * Tuotoksen tekijän tai tekijäryhmän nimi
     */
    creator: string;
    /**
     * Alusta jolla entry toimii. Voit jättää tyhjäksi jos entry ei sisällä ajettavaa koodia.
     */
    platform?: string | null;
    readonly entry_file_url: string | null;
    readonly source_file_url: string | null;
    readonly image_file_original_url: string | null;
    readonly image_file_thumbnail_url: string | null;
    readonly image_file_medium_url: string | null;
    readonly youtube_url: string | null;
    readonly disqualified: boolean | null;
    readonly disqualified_reason: string | null;
    readonly score: number | null;
    readonly rank: number | null;
    readonly alternate_files: Array<AlternateEntryFile>;
};
