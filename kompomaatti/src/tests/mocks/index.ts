import type { IEvent, ICompoEntry, ICompo, IUser, ICompetition } from 'src/api/interfaces';

export const mockUser: IUser = {
    id: 1234567,
    first_name: 'test',
    last_name: 'user',
    email: 'test.user@example.com'
};

export const mockEvent: IEvent = {
    id: 1,
    name: 'Intanssi 20017',
    date: '2018-02-08T20:31:43.000Z',
    mainurl: 'http://intanssi.org/20017',
};

export const mockCompoEntry: ICompoEntry = {
    id: 123,
    compo: 44,
    name: 'Stochastic Mock Coverage Tracer',
    description: '',
    creator: 'anon',
    platform: 'PC',
    entryfile_url: 'http://intanssi.org/files/123.zip',
    sourcefile_url: 'http://intanssi.org/files/123.src.zip',
    imagefile_original_url: 'http://intanssi.org/files/123.img.jpg',
    imagefile_thumbnail_url: 'http://intanssi.org/files/123.thumb.jpg',
    imagefile_medium_url: 'http://intanssi.org/files/123.med.jpg',
    youtube_url: 'http://youtube.com/foofoo',
    disqualified: false,
    disqualified_reason: '',
    score: 31.337,
    rank: 1,
};

export const mockCompo: ICompo = {
    id: 420,
    event: 10,
    name: 'Testing compo',
    description: 'Compo for testing',
    adding_end: '2018-02-06T00:00:00.000Z',
    editing_end: '2018-02-06T00:00:00.000Z',
    compo_start: '2018-02-06T00:00:00.000Z',
    voting_start: '2018-02-06T00:00:00.000Z',
    voting_end: '2018-02-06T00:00:00.000Z',
    max_source_size: 8 * 2 ** 20,
    max_entry_size: 16 * 2 ** 20,
    max_image_size: 2 * 2 ** 20,
    source_format_list: ['rar', 'zip', '7z', 'tar.gz'],
    entry_format_list: ['rar', 'zip', '7z', 'tar.gz'],
    image_format_list: ['png', 'jpg'],
    show_voting_results: false,
    entry_view_type: 1,
    is_votable: true,
    is_imagefile_allowed: true,
    is_imagefile_required: true,
};

export const mockCompetition: ICompetition = {
    id: 23452345,
    event: mockEvent.id,
    name: 'Bread Compo',
    description: 'Bread.',
    participation_end: '2026-02-27T20:00:00.000Z',
    start: '2026-02-27T19:00:00.000Z',
    end: '2026-02-27T21:00:00.000Z',
    /** Unit (plural) for scoring */
    score_type: 'crumbs',
    score_sort: 1,
    /** Are the results public yet? */
    show_results: false,
};
