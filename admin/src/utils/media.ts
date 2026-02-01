/**
 * Shared media utilities for file type detection
 */

export const IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "ico"];
export const VIDEO_EXTENSIONS = ["mp4", "mkv", "webm", "avi", "mov", "wmv", "flv", "ogv"];
export const AUDIO_EXTENSIONS = ["mp3", "ogg", "opus", "aac", "wav", "flac", "m4a", "wma"];

export type MediaType = "image" | "video" | "audio" | "other";

/**
 * Extract filename from a URL
 * @param url - The URL to extract filename from
 * @returns The filename or null if extraction fails
 */
export function getFilenameFromUrl(url: string | null): string | null {
    if (!url) return null;
    try {
        const pathname = new URL(url).pathname;
        return pathname.split("/").pop() || null;
    } catch {
        // If URL parsing fails, try to extract filename directly
        return url.split("/").pop()?.split("?")[0] || null;
    }
}

/**
 * Extract file extension from a filename
 * @param filename - The filename to extract extension from
 * @returns The lowercase extension or null if extraction fails
 */
export function getExtension(filename: string | null): string | null {
    if (!filename) return null;
    const ext = filename.split(".").pop()?.toLowerCase();
    return ext || null;
}

/**
 * Detect media type from a URL based on file extension
 * @param url - The URL to detect media type for
 * @returns The detected media type
 */
export function detectMediaType(url: string | null): MediaType {
    const filename = getFilenameFromUrl(url);
    const ext = getExtension(filename);

    if (!ext) return "other";

    if (IMAGE_EXTENSIONS.includes(ext)) return "image";
    if (VIDEO_EXTENSIONS.includes(ext)) return "video";
    if (AUDIO_EXTENSIONS.includes(ext)) return "audio";

    return "other";
}
