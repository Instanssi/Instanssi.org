
/**
 * Tries to guess if a URL refers to an image.
 * @param urlString URL to check.
 */
export function isImageURL(urlString: string): boolean {
    try {
        const url = new URL(urlString);
        const path = url.pathname.toLowerCase();
        return !!path.match(/(jpg|jpeg|png|webp|gif|bmp)$/);

    } catch (error) {
        console.error(error);
        return false;
    }
}

/**
 * Tries to guess if a URL refers to an audio file.
 * @param urlString URL to check.
 */
export function isAudioURL(urlString: string): boolean {
    try {
        const url = new URL(urlString);
        const path = url.pathname.toLowerCase();
        return !!path.match(/(mp3|ogg|opus|wav|flac)$/);

    } catch (error) {
        console.error(error);
        return false;
    }
}
