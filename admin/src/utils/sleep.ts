// Sleep utility function.

export function sleep(millis: number): Promise<void> {
    return new Promise((r) => setTimeout(r, millis));
}
