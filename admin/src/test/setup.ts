import { vi } from "vitest";

// Mock API - includes all admin endpoints used by form views
vi.mock("@/api", () => ({
    // Auth endpoints
    login: vi.fn(),
    logout: vi.fn(),
    userInfo: vi.fn(),

    // Audit log
    adminAuditlogList: vi.fn().mockResolvedValue({ data: { results: [], count: 0 } }),

    // Users
    adminUsersCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminUsersPartialUpdate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminUsersRetrieve: vi.fn().mockResolvedValue({ data: {} }),
    adminUsersList: vi.fn().mockResolvedValue({ data: { results: [] } }),

    // Events
    adminEventsCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventsPartialUpdate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventsRetrieve: vi.fn().mockResolvedValue({ data: {} }),

    // Blog
    adminBlogCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminBlogPartialUpdate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminBlogRetrieve: vi.fn().mockResolvedValue({ data: {} }),

    // Video categories
    adminEventArkistoVideoCategoriesCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventArkistoVideoCategoriesPartialUpdate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventArkistoVideoCategoriesRetrieve: vi.fn().mockResolvedValue({ data: {} }),
    adminEventArkistoVideoCategoriesList: vi.fn().mockResolvedValue({ data: { results: [] } }),

    // Videos
    adminEventArkistoVideosCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventArkistoVideosPartialUpdate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventArkistoVideosRetrieve: vi.fn().mockResolvedValue({ data: {} }),

    // Competitions
    adminEventKompomaattiCompetitionsCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventKompomaattiCompetitionsPartialUpdate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventKompomaattiCompetitionsRetrieve: vi.fn().mockResolvedValue({ data: {} }),
    adminEventKompomaattiCompetitionsList: vi.fn().mockResolvedValue({ data: { results: [] } }),

    // Competition participations
    adminEventKompomaattiCompetitionParticipationsCreate: vi
        .fn()
        .mockResolvedValue({ data: { id: 1 } }),
    adminEventKompomaattiCompetitionParticipationsPartialUpdate: vi
        .fn()
        .mockResolvedValue({ data: { id: 1 } }),
    adminEventKompomaattiCompetitionParticipationsRetrieve: vi.fn().mockResolvedValue({ data: {} }),

    // Compos
    adminEventKompomaattiComposCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventKompomaattiComposPartialUpdate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventKompomaattiComposRetrieve: vi.fn().mockResolvedValue({ data: {} }),
    adminEventKompomaattiComposList: vi.fn().mockResolvedValue({ data: { results: [] } }),

    // Entries
    adminEventKompomaattiEntriesCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventKompomaattiEntriesPartialUpdate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventKompomaattiEntriesRetrieve: vi.fn().mockResolvedValue({ data: {} }),

    // Program events
    adminEventProgramEventsCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventProgramEventsPartialUpdate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventProgramEventsRetrieve: vi.fn().mockResolvedValue({ data: {} }),

    // Uploads
    adminEventUploadsFilesCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventUploadsFilesPartialUpdate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventUploadsFilesRetrieve: vi.fn().mockResolvedValue({ data: {} }),

    // Store items
    adminEventStoreItemsCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventStoreItemsPartialUpdate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventStoreItemsRetrieve: vi.fn().mockResolvedValue({ data: {} }),
    adminEventStoreItemVariantsCreate: vi.fn().mockResolvedValue({ data: { id: 1 } }),
    adminEventStoreItemVariantsDestroy: vi.fn().mockResolvedValue({}),

    // Tokens
    tokensList: vi.fn().mockResolvedValue({ data: { results: [], count: 0 } }),
    tokensDestroy: vi.fn().mockResolvedValue({}),
    userTokensCreateToken: vi.fn().mockResolvedValue({
        data: {
            pk: "test-pk",
            token_key: "abc12345",
            token: "abc12345defgh67890ijklmnop123456qrstuvwxyz789012345678901234",
            created: "2024-01-15T10:00:00Z",
            expiry: "2024-02-14T10:00:00Z",
        },
    }),
}));

// Mock vue-router
vi.mock("vue-router", () => ({
    useRouter: () => ({
        push: vi.fn(),
        replace: vi.fn(),
    }),
    useRoute: () => ({
        params: {},
        query: {},
    }),
}));

// Mock vue-toastification
vi.mock("vue-toastification", () => ({
    useToast: () => ({
        success: vi.fn(),
        error: vi.fn(),
        warning: vi.fn(),
        info: vi.fn(),
    }),
}));

// Mock vue-i18n
vi.mock("vue-i18n", () => ({
    useI18n: () => ({
        t: (key: string) => key,
        d: (date: string) => date,
    }),
}));

// Mock events service
vi.mock("@/services/events", () => ({
    useEvents: () => ({
        getLatestEvent: () => ({ id: 1, name: "Test Event" }),
        getEventById: (id: number) => ({ id, name: `Event ${id}` }),
        refreshEvents: vi.fn(),
    }),
}));

// Mock auth service
vi.mock("@/services/auth", () => ({
    useAuth: () => ({
        isLoggedIn: () => true,
        canView: () => true,
        canAdd: () => true,
        canChange: () => true,
        canDelete: () => true,
        login: vi.fn(),
        logout: vi.fn(),
        refreshStatus: vi.fn(),
    }),
    PermissionTarget: {
        EVENT: "event",
        USER: "user",
        BLOG_ENTRY: "blogentry",
        AUTH_TOKEN: "authtoken",
        LOG_ENTRY: "logentry",
    },
}));

// Mock symbols (for inject)
vi.mock("@/symbols", () => ({
    confirmDialogKey: Symbol("confirmDialog"),
}));

// Mock VuetifyTiptap component
vi.mock("vuetify-pro-tiptap", () => ({
    VuetifyTiptap: {
        name: "VuetifyTiptap",
        template:
            '<textarea :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)"></textarea>',
        props: ["modelValue"],
        emits: ["update:modelValue"],
    },
    createVuetifyProTipTap: vi.fn(() => ({})),
}));
