// Attempts to describe the Instanssi REST API's objects go here.

/** Primary key (aka id) of a database record. */
export type PrimaryKey = number;
/** Some other record's primary key. */
export type ReferenceKey = number;
/** ISO 8601 date (not datetime), e.g. '2011-05-13'. */
export type ISODate = string;
/** ISO 8601 datetime with timezone part, e.g. '2013-03-03T15:10:00+02:00'. */
export type ISODateTime = string;
/** URL to something. */
export type URLString = string;
/** Fixed point decimal value encoded as a string. */
export type FixedPointNumber = string;

export interface IUser {
    id: PrimaryKey;
    first_name: string;
    last_name: string;
    email: string;
}

export interface IEvent {
    id: PrimaryKey;
    name: string;
    date: ISODate;
    mainurl: string;
}

export interface ICompetition {
    id: PrimaryKey;
    event: ReferenceKey;
    name: string;
    description: string;
    participation_end: ISODateTime;
    start: ISODateTime;
    end: ISODateTime;
    /** Unit (plural) for scoring */
    score_type: string;
    score_sort: number;
    /** Are the results public yet? */
    show_results: boolean;
}

export interface ICompetitionParticipation {
    id: PrimaryKey;
    competition: ReferenceKey;
    participant_name: string;
    score: number | null;
    rank: number | null;
    disqualified: boolean | null;
    disqualified_reason: string | null;
}

export interface ICompo {
    id: PrimaryKey;
    event: ReferenceKey;
    name: string;
    description: string;
    adding_end: ISODateTime;
    editing_end: ISODateTime;
    compo_start: ISODateTime;
    voting_start: ISODateTime;
    voting_end: ISODateTime;
    max_source_size: number;
    max_entry_size: number;
    max_image_size: number;
    source_format_list: string[];
    entry_format_list: string[];
    image_format_list: string[];
    show_voting_results: boolean;
    entry_view_type: number;
    is_votable: boolean;
    is_imagefile_allowed: boolean;
    is_imagefile_required: boolean;
}

export interface ICompoEntry {
    id: PrimaryKey;
    compo: ReferenceKey;
    name: string;
    description: string;
    creator: string;
    platform: string | null;
    entryfile_url: URLString | null;
    sourcefile_url: URLString | null;
    imagefile_original_url: URLString | null;
    imagefile_thumbnail_url: URLString | null;
    imagefile_medium_url: URLString | null;
    youtube_url: URLString | null;
    disqualified: boolean;
    disqualified_reason: string;
    score: number | null;
    rank: number | null;
}

export interface IUserCompoEntry {
    id: PrimaryKey;
    compo: ReferenceKey;
    name: string;
    description: string;
    creator: string;
    entryfile_url: URLString | null;
    sourcefile_url: URLString | null;
    imagefile_original_url: URLString | null;
    imagefile_thumbnail_url: URLString | null;
    imagefile_medium_url: URLString | null;
    disqualified: boolean;
    disqualified_reason: string;
}

export interface IProgrammeEvent {
    id: PrimaryKey;
    event: ReferenceKey;
    start: ISODateTime;
    end: ISODateTime | null;
    description: string;
    title: string;
    presenters: string;
    presenters_titles: string;
    place: string;
}

export interface ISponsor {
    id: PrimaryKey;
    event: ReferenceKey;
    name: string;
    logo_url: URLString | null;
    logo_scaled_url: URLString | null;
}

/** Messages to show on the big screen or whatever. */
export interface IMessage {
    id: PrimaryKey;
    event: ReferenceKey;
    show_start: ISODateTime;
    show_end: ISODateTime;
    text: string;
}

export interface IIRCMessage {
    id: PrimaryKey;
    event: ReferenceKey;
    date: ISODateTime;
    nick: string;
    message: string;
}

export interface IStoreItemVariant {
    id: PrimaryKey;
    name: string;
}

export interface IStoreItem {
    id: PrimaryKey;
    event: ReferenceKey;
    name: string;
    description: string;
    price: FixedPointNumber;
    max: number;
    available: boolean;
    imagefile_original_url: URLString | null;
    imagefile_thumbnail_url: URLString | null;
    max_per_order: number;
    sort_index: number;
    discount_amount: number;
    discount_percentage: number;
    is_discount_available: boolean;
    discount_factor: number;
    num_available: number;
    variants: IStoreItemVariant[];
}

export interface IVoteCodeRequest {
    id: PrimaryKey;
    event: ReferenceKey;
    text: string;
    /** 0 = pending, 1 = ok, 2 = rejected. */
    status: number;
}

export interface IVoteCode {
    id: PrimaryKey;
    event: ReferenceKey;
    time: ISODateTime;
    ticket_key: string;
}

export interface IUserVote {
    compo: ReferenceKey;
    entries: ReferenceKey[];
}
