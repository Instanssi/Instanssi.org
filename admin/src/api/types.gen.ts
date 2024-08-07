// This file is auto-generated by @hey-api/openapi-ts

export type AlternateEntryFile = {
    readonly format: string;
    readonly url: string;
};

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
    readonly created_by: string;
};

export type BlogEntryRequest = {
    user?: number;
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

export type CompoEntryRequest = {
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
};

export type Event = {
    readonly id: number;
    /**
     * Tapahtuman nimi
     */
    name: string;
    /**
     * Lyhyt nimi, eg. vuosi
     */
    tag?: string | null;
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

export type EventRequest = {
    /**
     * Tapahtuman nimi
     */
    name: string;
    /**
     * Lyhyt nimi, eg. vuosi
     */
    tag?: string | null;
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

export type Group = {
    name: string;
};

export type GroupRequest = {
    name: string;
};

export type PaginatedBlogEntryList = {
    count: number;
    next?: string | null;
    previous?: string | null;
    results: Array<BlogEntry>;
};

export type PaginatedCompoEntryList = {
    count: number;
    next?: string | null;
    previous?: string | null;
    results: Array<CompoEntry>;
};

export type PaginatedEventList = {
    count: number;
    next?: string | null;
    previous?: string | null;
    results: Array<Event>;
};

export type PaginatedUserList = {
    count: number;
    next?: string | null;
    previous?: string | null;
    results: Array<User>;
};

export type PatchedBlogEntryRequest = {
    user?: number;
    /**
     * Lyhyt otsikko entrylle.
     */
    title?: string;
    text?: string;
    /**
     * Mikäli entry on julkinen, tulee se näkyviin sekä tapahtuman sivuille että RSS-syötteeseen.
     */
    public?: boolean;
    event?: number;
};

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

export type PatchedEventRequest = {
    /**
     * Tapahtuman nimi
     */
    name?: string;
    /**
     * Lyhyt nimi, eg. vuosi
     */
    tag?: string | null;
    /**
     * Tapahtuman päivämäärä (alku)
     */
    date?: string;
    /**
     * Saa näyttää arkistossa
     */
    archived?: boolean;
    /**
     * URL Tapahtuman pääsivustolle
     */
    mainurl?: string;
};

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

export type Permission = {
    name: string;
    codename: string;
};

export type PermissionRequest = {
    name: string;
    codename: string;
};

export type SocialAuthURL = {
    method: string;
    url: string;
    name: string;
};

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

export type UserLoginRequest = {
    username: string;
    password: string;
};

export type UserRequest = {
    /**
     * Vaaditaan. Enintään 150 merkkiä. Vain kirjaimet, numerot ja @/./+/-/_ ovat sallittuja.
     */
    username: string;
    first_name?: string;
    last_name?: string;
    email?: string;
    /**
     * Määrää, voiko käyttäjä kirjautua sisään. Tällä voi estää käyttäjätilin käytön poistamatta sitä.
     */
    is_active?: boolean;
};

export type $OpenApiTs = {
    "/api/v2/auth/login/": {
        post: {
            req: {
                requestBody: UserLoginRequest;
            };
            res: {
                /**
                 * No response body
                 */
                204: void;
            };
        };
    };
    "/api/v2/auth/logout/": {
        post: {
            res: {
                /**
                 * No response body
                 */
                204: void;
            };
        };
    };
    "/api/v2/auth/social_urls/": {
        get: {
            req: {
                next?: string;
            };
            res: {
                200: Array<SocialAuthURL>;
            };
        };
    };
    "/api/v2/blog_entries/": {
        get: {
            req: {
                event?: number;
                /**
                 * Number of results to return per page.
                 */
                limit?: number;
                /**
                 * The initial index from which to return the results.
                 */
                offset?: number;
                /**
                 * Which field to use when ordering the results.
                 */
                ordering?: string;
                /**
                 * A search term.
                 */
                search?: string;
                user?: number;
            };
            res: {
                200: PaginatedBlogEntryList;
            };
        };
        post: {
            req: {
                requestBody: BlogEntryRequest;
            };
            res: {
                201: BlogEntry;
            };
        };
    };
    "/api/v2/blog_entries/{id}/": {
        get: {
            req: {
                /**
                 * A unique integer value identifying this entry.
                 */
                id: number;
            };
            res: {
                200: BlogEntry;
            };
        };
        put: {
            req: {
                /**
                 * A unique integer value identifying this entry.
                 */
                id: number;
                requestBody: BlogEntryRequest;
            };
            res: {
                200: BlogEntry;
            };
        };
        patch: {
            req: {
                /**
                 * A unique integer value identifying this entry.
                 */
                id: number;
                requestBody?: PatchedBlogEntryRequest;
            };
            res: {
                200: BlogEntry;
            };
        };
        delete: {
            req: {
                /**
                 * A unique integer value identifying this entry.
                 */
                id: number;
            };
            res: {
                /**
                 * No response body
                 */
                204: void;
            };
        };
    };
    "/api/v2/events/": {
        get: {
            req: {
                /**
                 * Number of results to return per page.
                 */
                limit?: number;
                name?: string;
                /**
                 * The initial index from which to return the results.
                 */
                offset?: number;
                /**
                 * Which field to use when ordering the results.
                 */
                ordering?: string;
            };
            res: {
                200: PaginatedEventList;
            };
        };
        post: {
            req: {
                requestBody: EventRequest;
            };
            res: {
                201: Event;
            };
        };
    };
    "/api/v2/events/{id}/": {
        get: {
            req: {
                /**
                 * A unique integer value identifying this tapahtuma.
                 */
                id: number;
            };
            res: {
                200: Event;
            };
        };
        put: {
            req: {
                /**
                 * A unique integer value identifying this tapahtuma.
                 */
                id: number;
                requestBody: EventRequest;
            };
            res: {
                200: Event;
            };
        };
        patch: {
            req: {
                /**
                 * A unique integer value identifying this tapahtuma.
                 */
                id: number;
                requestBody?: PatchedEventRequest;
            };
            res: {
                200: Event;
            };
        };
        delete: {
            req: {
                /**
                 * A unique integer value identifying this tapahtuma.
                 */
                id: number;
            };
            res: {
                /**
                 * No response body
                 */
                204: void;
            };
        };
    };
    "/api/v2/user_compo_entries/": {
        get: {
            req: {
                /**
                 * Number of results to return per page.
                 */
                limit?: number;
                /**
                 * The initial index from which to return the results.
                 */
                offset?: number;
                /**
                 * Which field to use when ordering the results.
                 */
                ordering?: string;
            };
            res: {
                200: PaginatedCompoEntryList;
            };
        };
        post: {
            req: {
                formData: CompoEntryRequest;
            };
            res: {
                201: CompoEntry;
            };
        };
    };
    "/api/v2/user_compo_entries/{id}/": {
        get: {
            req: {
                id: string;
            };
            res: {
                200: CompoEntry;
            };
        };
        put: {
            req: {
                formData: CompoEntryRequest;
                id: string;
            };
            res: {
                200: CompoEntry;
            };
        };
        patch: {
            req: {
                formData?: PatchedCompoEntryRequest;
                id: string;
            };
            res: {
                200: CompoEntry;
            };
        };
        delete: {
            req: {
                id: string;
            };
            res: {
                /**
                 * No response body
                 */
                204: void;
            };
        };
    };
    "/api/v2/user_info/": {
        get: {
            res: {
                200: Array<UserInfo>;
            };
        };
    };
    "/api/v2/users/": {
        get: {
            req: {
                email?: string;
                /**
                 * Number of results to return per page.
                 */
                limit?: number;
                /**
                 * The initial index from which to return the results.
                 */
                offset?: number;
                /**
                 * Which field to use when ordering the results.
                 */
                ordering?: string;
                /**
                 * A search term.
                 */
                search?: string;
                username?: string;
            };
            res: {
                200: PaginatedUserList;
            };
        };
        post: {
            req: {
                requestBody: UserRequest;
            };
            res: {
                201: User;
            };
        };
    };
    "/api/v2/users/{id}/": {
        get: {
            req: {
                /**
                 * A unique integer value identifying this käyttäjä.
                 */
                id: number;
            };
            res: {
                200: User;
            };
        };
        put: {
            req: {
                /**
                 * A unique integer value identifying this käyttäjä.
                 */
                id: number;
                requestBody: UserRequest;
            };
            res: {
                200: User;
            };
        };
        patch: {
            req: {
                /**
                 * A unique integer value identifying this käyttäjä.
                 */
                id: number;
                requestBody?: PatchedUserRequest;
            };
            res: {
                200: User;
            };
        };
        delete: {
            req: {
                /**
                 * A unique integer value identifying this käyttäjä.
                 */
                id: number;
            };
            res: {
                /**
                 * No response body
                 */
                204: void;
            };
        };
    };
};
