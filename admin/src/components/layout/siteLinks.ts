/** External Django-side pages linked from the admin top bar. */
export type SiteLink = {
    titleKey: string;
    href: string;
};

export const SITE_LINKS: SiteLink[] = [
    { titleKey: "MainNavigation.links.index", href: "/" },
    { titleKey: "MainNavigation.links.kompomaatti", href: "/kompomaatti/" },
    { titleKey: "MainNavigation.links.arkisto", href: "/arkisto/" },
];
