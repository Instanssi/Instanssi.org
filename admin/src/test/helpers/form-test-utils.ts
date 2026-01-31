import type { VueWrapper } from "@vue/test-utils";
import { flushPromises } from "@vue/test-utils";
import type { AxiosError } from "axios";
import { expect } from "vitest";

/**
 * Wait for vee-validate validation to complete.
 * This is needed because vee-validate uses microtasks for validation.
 */
export async function waitForValidation(): Promise<void> {
    await flushPromises();
    await new Promise((resolve) => setTimeout(resolve, 10));
    await flushPromises();
}

/**
 * Submit a form by clicking the save button.
 * Includes waiting for validation to complete before and after clicking.
 *
 * @param wrapper - The mounted component wrapper
 * @param buttonText - Text to find the button (default: 'General.save')
 */
export async function submitForm(
    wrapper: VueWrapper,
    buttonText: string = "General.save"
): Promise<void> {
    // Wait for any pending validation
    await waitForValidation();

    // Submit by clicking the save button
    const buttons = wrapper.findAllComponents({ name: "VBtn" });
    const saveButton = buttons.find((b) => b.text().includes(buttonText));
    if (saveButton) {
        await saveButton.trigger("click");
    }

    // Wait for async submit to complete
    await waitForValidation();
}

/**
 * Create a mock API error response for testing error handling.
 *
 * @param status - HTTP status code (default 400)
 * @param fieldErrors - Object mapping field names to error messages
 * @returns Mock error object matching AxiosError structure
 */
export function createMockApiError(
    status: number = 400,
    fieldErrors: Record<string, string[]> = {}
): AxiosError {
    return {
        response: {
            status,
            data: fieldErrors,
        },
    } as AxiosError;
}

/**
 * Create a mock API error with a detail message.
 *
 * @param status - HTTP status code
 * @param detail - Detail message string
 * @returns Mock error object
 */
export function createMockApiDetailError(status: number, detail: string): AxiosError {
    return {
        response: {
            status,
            data: { detail },
        },
    } as AxiosError;
}

/**
 * Assert that an API mock was called with specific body contents.
 * Works with both JSON and FormData body types.
 *
 * @param mockFn - The mocked API function
 * @param expectedBody - Expected body contents (partial match)
 */
export function expectApiCalledWithBody(
    mockFn: ReturnType<typeof import("vitest").vi.fn>,
    expectedBody: Record<string, unknown>
): void {
    expect(mockFn).toHaveBeenCalled();
    const call = mockFn.mock.calls[0];
    expect(call).toBeDefined();
    const callArgs = call![0] as { body: Record<string, unknown> };
    const actualBody = callArgs.body;

    for (const [key, value] of Object.entries(expectedBody)) {
        expect(actualBody[key]).toEqual(value);
    }
}

/**
 * Assert that an API mock was called with specific path parameters.
 *
 * @param mockFn - The mocked API function
 * @param expectedPath - Expected path parameters
 */
export function expectApiCalledWithPath(
    mockFn: ReturnType<typeof import("vitest").vi.fn>,
    expectedPath: Record<string, unknown>
): void {
    expect(mockFn).toHaveBeenCalled();
    const call = mockFn.mock.calls[0];
    expect(call).toBeDefined();
    const callArgs = call![0] as { path: Record<string, unknown> };
    expect(callArgs.path).toEqual(expectedPath);
}

/**
 * Get the body from the most recent API call.
 *
 * @param mockFn - The mocked API function
 * @returns The body object from the call
 */
export function getApiCallBody(
    mockFn: ReturnType<typeof import("vitest").vi.fn>
): Record<string, unknown> {
    expect(mockFn).toHaveBeenCalled();
    const call = mockFn.mock.calls[0];
    expect(call).toBeDefined();
    return (call![0] as { body: Record<string, unknown> }).body;
}

/**
 * Get the serialized body (FormData) from the most recent API call.
 * Calls the bodySerializer if present.
 *
 * @param mockFn - The mocked API function
 * @returns FormData or the raw body
 */
export function getSerializedApiCallBody(
    mockFn: ReturnType<typeof import("vitest").vi.fn>
): FormData | Record<string, unknown> {
    expect(mockFn).toHaveBeenCalled();
    const call = mockFn.mock.calls[0];
    expect(call).toBeDefined();
    const callArgs = call![0] as {
        body: Record<string, unknown>;
        bodySerializer?: (body: Record<string, unknown>) => FormData;
    };
    if (callArgs.bodySerializer) {
        return callArgs.bodySerializer(callArgs.body);
    }
    return callArgs.body;
}
