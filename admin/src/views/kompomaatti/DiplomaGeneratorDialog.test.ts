import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import * as api from "@/api";

import DiplomaGeneratorDialog from "./DiplomaGeneratorDialog.vue";

vi.mock("@/api");
vi.mock("vue-toastification", () => ({
    useToast: () => ({
        success: vi.fn(),
        error: vi.fn(),
    }),
}));
vi.mock("@/services/events", () => ({
    useEvents: () => ({
        getEventById: vi.fn().mockReturnValue({ id: 1, name: "Test Event 2024" }),
    }),
}));

const vuetify = createVuetify({ components, directives });

const mockUploads = {
    data: {
        results: [
            { id: 1, filename: "background.png", file_url: "https://example.com/background.png" },
            { id: 2, filename: "image.jpg", file_url: "https://example.com/image.jpg" },
            { id: 3, filename: "document.pdf", file_url: "https://example.com/document.pdf" },
        ],
    },
};

const mockCompos = {
    data: {
        results: [
            { id: 1, name: "Demo Compo" },
            { id: 2, name: "Music Compo" },
        ],
    },
};

const mockEntries = {
    data: {
        results: [
            { id: 1, compo: 1, name: "Cool Demo", creator: "Artist One", computed_rank: 1 },
            { id: 2, compo: 1, name: "Nice Demo", creator: "Artist Two", computed_rank: 2 },
            { id: 3, compo: 1, name: "Demo Three", creator: "Artist Three", computed_rank: 3 },
            { id: 4, compo: 1, name: "Demo Four", creator: "Artist Four", computed_rank: 4 },
            { id: 5, compo: 2, name: "Great Track", creator: "Musician One", computed_rank: 1 },
            { id: 6, compo: 2, name: "Nice Track", creator: "Team A / Team B", computed_rank: 2 },
        ],
    },
};

const mockCompetitions = {
    data: {
        results: [
            { id: 1, name: "Fast Typing" },
            { id: 2, name: "Quiz" },
        ],
    },
};

const mockParticipations = {
    data: {
        results: [
            { id: 1, competition: 1, participant_name: "Speedy", computed_rank: 1 },
            { id: 2, competition: 1, participant_name: "Quick", computed_rank: 2 },
            { id: 3, competition: 2, participant_name: "Smart One", computed_rank: 1 },
        ],
    },
};

// Helper type for accessing internal component state
interface DialogInternals {
    backgroundOptions: Array<{ title: string; value: string }>;
    diplomaDataList: Array<{
        author: string;
        entryName: string | null;
        placement: string;
        compoName: string;
        hasMultipleAuthors: boolean;
    }>;
    canGenerate: boolean;
    selectedBackground: string | null;
    noEntriesWarning: boolean;
    mainOrganizerTitle: string;
    programOrganizerTitle: string;
}

function mountComponent(props: { eventId: number }) {
    return mount(DiplomaGeneratorDialog, {
        props,
        global: {
            plugins: [vuetify],
            stubs: {
                FontAwesomeIcon: true,
                BaseDialog: {
                    template: '<div class="base-dialog"><slot /></div>',
                    methods: {
                        modal: vi.fn(),
                        setResult: vi.fn(),
                    },
                },
                ImageSelectField: true,
            },
        },
    });
}

describe("DiplomaGeneratorDialog", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.mocked(api.adminEventUploadsFilesList).mockResolvedValue(mockUploads as never);
        vi.mocked(api.adminEventKompomaattiComposList).mockResolvedValue(mockCompos as never);
        vi.mocked(api.adminEventKompomaattiEntriesList).mockResolvedValue(mockEntries as never);
        vi.mocked(api.adminEventKompomaattiCompetitionsList).mockResolvedValue(
            mockCompetitions as never
        );
        vi.mocked(api.adminEventKompomaattiCompetitionParticipationsList).mockResolvedValue(
            mockParticipations as never
        );
    });

    describe("rendering", () => {
        it("renders the dialog component", async () => {
            const wrapper = mountComponent({ eventId: 1 });
            await flushPromises();

            expect(wrapper.find(".base-dialog").exists()).toBe(true);
        });

        it("renders organizer input fields", async () => {
            const wrapper = mountComponent({ eventId: 1 });
            await flushPromises();

            const textFields = wrapper.findAllComponents({ name: "VTextField" });
            expect(textFields.length).toBe(4); // 4 organizer fields
        });

        it("renders include checkboxes", async () => {
            const wrapper = mountComponent({ eventId: 1 });
            await flushPromises();

            const checkboxes = wrapper.findAllComponents({ name: "VCheckbox" });
            expect(checkboxes.length).toBe(2); // compos and competitions
        });
    });

    describe("data loading", () => {
        it("loads all data when dialog opens", async () => {
            const wrapper = mountComponent({ eventId: 1 });

            // Call open method
            wrapper.vm.open();
            await flushPromises();

            expect(api.adminEventUploadsFilesList).toHaveBeenCalledWith({
                path: { event_pk: 1 },
                query: { limit: 100 },
            });
            expect(api.adminEventKompomaattiEntriesList).toHaveBeenCalledWith({
                path: { event_pk: 1 },
                query: { limit: 10000 },
            });
            expect(api.adminEventKompomaattiComposList).toHaveBeenCalledWith({
                path: { event_pk: 1 },
                query: { limit: 100 },
            });
            expect(api.adminEventKompomaattiCompetitionsList).toHaveBeenCalledWith({
                path: { event_pk: 1 },
                query: { limit: 100 },
            });
            expect(api.adminEventKompomaattiCompetitionParticipationsList).toHaveBeenCalledWith({
                path: { event_pk: 1 },
                query: { limit: 10000 },
            });
        });
    });

    describe("background image filtering", () => {
        it("filters uploads to only show image files", async () => {
            const wrapper = mountComponent({ eventId: 1 });
            wrapper.vm.open();
            await flushPromises();

            // Access computed property via component instance
            const vm = wrapper.vm as unknown as DialogInternals;

            // Should only include .png and .jpg files, not .pdf
            expect(vm.backgroundOptions).toHaveLength(2);
            expect(vm.backgroundOptions.map((o) => o.title)).toContain("background.png");
            expect(vm.backgroundOptions.map((o) => o.title)).toContain("image.jpg");
            expect(vm.backgroundOptions.map((o) => o.title)).not.toContain("document.pdf");
        });
    });

    describe("diploma data generation", () => {
        it("generates diploma data for top 3 entries per compo", async () => {
            const wrapper = mountComponent({ eventId: 1 });
            wrapper.vm.open();
            await flushPromises();

            const vm = wrapper.vm as unknown as DialogInternals;

            // Demo Compo should have 3 entries (ranks 1, 2, 3), Music Compo should have 2
            // Plus competitions: Fast Typing has 2 (ranks 1, 2), Quiz has 1 (rank 1)
            // Total: 3 + 2 + 2 + 1 = 8

            // Check demo compo entries
            const demoEntries = vm.diplomaDataList.filter((d) => d.compoName === "Demo Compo");
            expect(demoEntries).toHaveLength(3);
            expect(demoEntries.map((d) => d.placement)).toEqual(["I", "II", "III"]);

            // Rank 4 should not be included
            const rank4Entry = vm.diplomaDataList.find((d) => d.author === "Artist Four");
            expect(rank4Entry).toBeUndefined();
        });

        it("detects multiple authors correctly", async () => {
            const wrapper = mountComponent({ eventId: 1 });
            wrapper.vm.open();
            await flushPromises();

            const vm = wrapper.vm as unknown as DialogInternals;

            // "Team A / Team B" should have hasMultipleAuthors = true
            const teamEntry = vm.diplomaDataList.find((d) => d.author === "Team A / Team B");
            expect(teamEntry?.hasMultipleAuthors).toBe(true);

            // Single author should have hasMultipleAuthors = false
            const singleEntry = vm.diplomaDataList.find((d) => d.author === "Artist One");
            expect(singleEntry?.hasMultipleAuthors).toBe(false);
        });

        it("includes competition participations when enabled", async () => {
            const wrapper = mountComponent({ eventId: 1 });
            wrapper.vm.open();
            await flushPromises();

            const vm = wrapper.vm as unknown as DialogInternals;

            // Competition entries should have null entryName
            const competitionEntries = vm.diplomaDataList.filter((d) => d.entryName === null);
            expect(competitionEntries.length).toBeGreaterThan(0);

            // Check specific competition entry
            const typingEntry = competitionEntries.find((d) => d.compoName === "Fast Typing");
            expect(typingEntry).toBeTruthy();
            expect(typingEntry?.author).toBe("Speedy");
        });

        it("excludes compo entries when includeCompos is false", async () => {
            const wrapper = mountComponent({ eventId: 1 });
            wrapper.vm.open();
            await flushPromises();

            // Find and uncheck the includeCompos checkbox
            const checkboxes = wrapper.findAllComponents({ name: "VCheckbox" });
            const compoCheckbox = checkboxes[0];
            if (compoCheckbox) {
                await compoCheckbox.vm.$emit("update:modelValue", false);
                await flushPromises();
            }

            const vm = wrapper.vm as unknown as DialogInternals;

            // Should only have competition entries (null entryName)
            const compoEntries = vm.diplomaDataList.filter((d) => d.entryName !== null);
            expect(compoEntries).toHaveLength(0);
        });

        it("excludes competition entries when includeCompetitions is false", async () => {
            const wrapper = mountComponent({ eventId: 1 });
            wrapper.vm.open();
            await flushPromises();

            // Find and uncheck the includeCompetitions checkbox
            const checkboxes = wrapper.findAllComponents({ name: "VCheckbox" });
            const competitionCheckbox = checkboxes[1];
            if (competitionCheckbox) {
                await competitionCheckbox.vm.$emit("update:modelValue", false);
                await flushPromises();
            }

            const vm = wrapper.vm as unknown as DialogInternals;

            // Should only have compo entries (non-null entryName)
            const competitionEntries = vm.diplomaDataList.filter((d) => d.entryName === null);
            expect(competitionEntries).toHaveLength(0);
        });
    });

    describe("validation", () => {
        it("disables generate button when no background is selected", async () => {
            const wrapper = mountComponent({ eventId: 1 });
            wrapper.vm.open();
            await flushPromises();

            const vm = wrapper.vm as unknown as DialogInternals;

            // No background selected by default
            expect(vm.selectedBackground).toBeNull();
            expect(vm.canGenerate).toBe(false);
        });

        it("shows warning when no entries are available", async () => {
            vi.mocked(api.adminEventKompomaattiEntriesList).mockResolvedValue({
                data: { results: [] },
            } as never);
            vi.mocked(api.adminEventKompomaattiCompetitionParticipationsList).mockResolvedValue({
                data: { results: [] },
            } as never);

            const wrapper = mountComponent({ eventId: 1 });
            wrapper.vm.open();
            await flushPromises();

            const vm = wrapper.vm as unknown as DialogInternals;
            expect(vm.noEntriesWarning).toBe(true);
        });
    });

    describe("organizer fields", () => {
        it("has default organizer titles in Finnish", async () => {
            const wrapper = mountComponent({ eventId: 1 });
            await flushPromises();

            const vm = wrapper.vm as unknown as DialogInternals;

            expect(vm.mainOrganizerTitle).toBe("Pääjärjestäjä");
            expect(vm.programOrganizerTitle).toBe("Ohjelmavastaava");
        });
    });
});
