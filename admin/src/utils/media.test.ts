import { describe, it, expect } from "vitest";
import {
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    AUDIO_EXTENSIONS,
    getFilenameFromUrl,
    getExtension,
    detectMediaType,
} from "./media";

describe("media utilities", () => {
    describe("extension constants", () => {
        it("contains common image extensions", () => {
            expect(IMAGE_EXTENSIONS).toContain("jpg");
            expect(IMAGE_EXTENSIONS).toContain("jpeg");
            expect(IMAGE_EXTENSIONS).toContain("png");
            expect(IMAGE_EXTENSIONS).toContain("gif");
            expect(IMAGE_EXTENSIONS).toContain("webp");
            expect(IMAGE_EXTENSIONS).toContain("svg");
        });

        it("contains common video extensions", () => {
            expect(VIDEO_EXTENSIONS).toContain("mp4");
            expect(VIDEO_EXTENSIONS).toContain("webm");
            expect(VIDEO_EXTENSIONS).toContain("mkv");
            expect(VIDEO_EXTENSIONS).toContain("mov");
        });

        it("contains common audio extensions", () => {
            expect(AUDIO_EXTENSIONS).toContain("mp3");
            expect(AUDIO_EXTENSIONS).toContain("ogg");
            expect(AUDIO_EXTENSIONS).toContain("wav");
            expect(AUDIO_EXTENSIONS).toContain("flac");
        });
    });

    describe("getFilenameFromUrl", () => {
        it("returns null for null input", () => {
            expect(getFilenameFromUrl(null)).toBeNull();
        });

        it("returns null for empty string", () => {
            expect(getFilenameFromUrl("")).toBeNull();
        });

        it("extracts filename from simple URL", () => {
            expect(getFilenameFromUrl("https://example.com/path/image.jpg")).toBe("image.jpg");
        });

        it("extracts filename from URL with query string", () => {
            expect(getFilenameFromUrl("https://example.com/path/image.jpg?v=123")).toBe(
                "image.jpg"
            );
        });

        it("extracts filename from URL with hash", () => {
            expect(getFilenameFromUrl("https://example.com/path/image.jpg#section")).toBe(
                "image.jpg"
            );
        });

        it("extracts filename from path-only URL", () => {
            expect(getFilenameFromUrl("/media/uploads/file.pdf")).toBe("file.pdf");
        });

        it("handles URL with multiple path segments", () => {
            expect(getFilenameFromUrl("https://example.com/a/b/c/d/e/file.zip")).toBe("file.zip");
        });

        it("handles URL with encoded characters", () => {
            expect(getFilenameFromUrl("https://example.com/path/my%20file.jpg")).toBe(
                "my%20file.jpg"
            );
        });

        it("returns null for URL with no path", () => {
            expect(getFilenameFromUrl("https://example.com/")).toBeNull();
        });

        it("handles malformed URL by falling back to string split", () => {
            expect(getFilenameFromUrl("not-a-url/file.jpg")).toBe("file.jpg");
        });
    });

    describe("getExtension", () => {
        it("returns null for null input", () => {
            expect(getExtension(null)).toBeNull();
        });

        it("returns null for empty string", () => {
            expect(getExtension("")).toBeNull();
        });

        it("extracts extension from filename", () => {
            expect(getExtension("image.jpg")).toBe("jpg");
        });

        it("returns lowercase extension", () => {
            expect(getExtension("image.JPG")).toBe("jpg");
            expect(getExtension("image.Png")).toBe("png");
        });

        it("handles multiple dots in filename", () => {
            expect(getExtension("archive.tar.gz")).toBe("gz");
        });

        it("handles filename with no extension", () => {
            expect(getExtension("filename")).toBe("filename");
        });

        it("handles filename with dot but no extension", () => {
            // Empty string after the dot is falsy, so null is returned
            expect(getExtension("file.")).toBeNull();
        });
    });

    describe("detectMediaType", () => {
        it("returns 'other' for null input", () => {
            expect(detectMediaType(null)).toBe("other");
        });

        it("returns 'other' for empty string", () => {
            expect(detectMediaType("")).toBe("other");
        });

        describe("image detection", () => {
            it.each(IMAGE_EXTENSIONS)("detects .%s as image", (ext) => {
                expect(detectMediaType(`https://example.com/file.${ext}`)).toBe("image");
            });

            it("detects uppercase extensions as image", () => {
                expect(detectMediaType("https://example.com/file.PNG")).toBe("image");
                expect(detectMediaType("https://example.com/file.JPG")).toBe("image");
            });
        });

        describe("video detection", () => {
            it.each(VIDEO_EXTENSIONS)("detects .%s as video", (ext) => {
                expect(detectMediaType(`https://example.com/file.${ext}`)).toBe("video");
            });

            it("detects uppercase extensions as video", () => {
                expect(detectMediaType("https://example.com/file.MP4")).toBe("video");
                expect(detectMediaType("https://example.com/file.WEBM")).toBe("video");
            });
        });

        describe("audio detection", () => {
            it.each(AUDIO_EXTENSIONS)("detects .%s as audio", (ext) => {
                expect(detectMediaType(`https://example.com/file.${ext}`)).toBe("audio");
            });

            it("detects uppercase extensions as audio", () => {
                expect(detectMediaType("https://example.com/file.MP3")).toBe("audio");
                expect(detectMediaType("https://example.com/file.WAV")).toBe("audio");
            });
        });

        describe("other file detection", () => {
            it("returns 'other' for PDF files", () => {
                expect(detectMediaType("https://example.com/document.pdf")).toBe("other");
            });

            it("returns 'other' for ZIP files", () => {
                expect(detectMediaType("https://example.com/archive.zip")).toBe("other");
            });

            it("returns 'other' for text files", () => {
                expect(detectMediaType("https://example.com/readme.txt")).toBe("other");
            });

            it("returns 'other' for executable files", () => {
                expect(detectMediaType("https://example.com/program.exe")).toBe("other");
            });

            it("returns 'other' for unknown extensions", () => {
                expect(detectMediaType("https://example.com/file.xyz")).toBe("other");
            });
        });

        it("handles URL with query parameters", () => {
            expect(detectMediaType("https://example.com/image.png?v=123")).toBe("image");
        });

        it("handles relative URLs", () => {
            expect(detectMediaType("/media/uploads/video.mp4")).toBe("video");
        });
    });
});
