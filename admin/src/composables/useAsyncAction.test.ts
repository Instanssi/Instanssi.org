import { beforeEach, describe, expect, it, vi } from "vitest";

const mockSuccess = vi.fn();
const mockError = vi.fn();

vi.mock("vue-toastification", () => ({
    useToast: () => ({
        success: mockSuccess,
        error: mockError,
    }),
}));

// Import after mocks are set up
const { useAsyncAction } = await import("./useAsyncAction");

describe("useAsyncAction", () => {
    beforeEach(() => {
        mockSuccess.mockClear();
        mockError.mockClear();
    });

    it("initializes with loading = false", () => {
        const { loading } = useAsyncAction({
            successMessage: "Done",
            failureMessage: "Failed",
        });
        expect(loading.value).toBe(false);
    });

    it("sets loading to true while running", async () => {
        const { loading, run } = useAsyncAction({
            successMessage: "Done",
            failureMessage: "Failed",
        });

        let loadingDuringRun = false;
        await run(() => {
            loadingDuringRun = loading.value;
        });

        expect(loadingDuringRun).toBe(true);
        expect(loading.value).toBe(false);
    });

    it("shows success toast on successful action", async () => {
        const { run } = useAsyncAction({
            successMessage: "Export complete!",
            failureMessage: "Export failed",
        });

        await run(() => {});

        expect(mockSuccess).toHaveBeenCalledWith("Export complete!");
        expect(mockError).not.toHaveBeenCalled();
    });

    it("shows error toast when action throws", async () => {
        const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
        const { run } = useAsyncAction({
            successMessage: "Done",
            failureMessage: "Something went wrong",
        });

        await run(() => {
            throw new Error("Network error");
        });

        expect(mockError).toHaveBeenCalledWith("Something went wrong");
        expect(mockSuccess).not.toHaveBeenCalled();
        consoleSpy.mockRestore();
    });

    it("logs error to console when action throws", async () => {
        const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
        const { run } = useAsyncAction({
            successMessage: "Done",
            failureMessage: "Failed",
        });

        const error = new Error("Network error");
        await run(() => {
            throw error;
        });

        expect(consoleSpy).toHaveBeenCalledWith(error);
        consoleSpy.mockRestore();
    });

    it("resets loading to false after error", async () => {
        const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
        const { loading, run } = useAsyncAction({
            successMessage: "Done",
            failureMessage: "Failed",
        });

        await run(() => {
            throw new Error("fail");
        });

        expect(loading.value).toBe(false);
        consoleSpy.mockRestore();
    });

    it("handles async functions", async () => {
        const { run } = useAsyncAction({
            successMessage: "Done",
            failureMessage: "Failed",
        });

        let executed = false;
        await run(async () => {
            await new Promise((resolve) => setTimeout(resolve, 1));
            executed = true;
        });

        expect(executed).toBe(true);
        expect(mockSuccess).toHaveBeenCalledWith("Done");
    });

    it("handles async functions that reject", async () => {
        const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
        const { loading, run } = useAsyncAction({
            successMessage: "Done",
            failureMessage: "Async failed",
        });

        await run(async () => {
            throw new Error("async error");
        });

        expect(mockError).toHaveBeenCalledWith("Async failed");
        expect(loading.value).toBe(false);
        consoleSpy.mockRestore();
    });
});
