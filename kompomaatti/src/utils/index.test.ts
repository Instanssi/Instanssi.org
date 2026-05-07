import { isImageURL, isAudioURL } from './';
import { test, expect } from 'vitest';

const audioUrls = [
    [false, 'https://test.test/stuff/image.jpg'],
    [false, 'http://test.test/a/b/c/thumb.jpeg'],
    [false, 'test://test.test/stuff/image.png'],
    [false, 'http://test.test/stuff/file.gif?query=ogg'],
    [true, 'https://test.test/stuff/audio.mp3'],
    [true, 'https://test.test/stuff/file.opus?foo=bar'],
    [true, 'spdy://host.srvr/classic.wav'],
    [true, 'ftp://host.srvr/classic.flac'],
    [true, 'test://host.srvr/something/file.ogg#'],
] as const;

test.each(audioUrls)('Recognizes audio files in URLs', (isAudio, urlString) => {
    expect(isAudioURL(urlString)).toBe(isAudio);
});

const imageUrls = [
    [true, 'https://test.test/stuff/image.jpg'],
    [true, 'http://test.test/a/b/c/thumb.jpeg'],
    [true, 'https://test.test/stuff/image.png'],
    [true, 'https://test.test/stuff/file.gif?query=ogg'],
    [true, 'http://test.test/uploads/thumb.webp'],
    [true, 'http://test.test/uploads/wat.bmp'],
    [false, 'https://test.test/stuff/audio.mp3'],
    [false, 'https://test.test/stuff/file.opus?foo=bar'],
    [false, 'spdy://host.srvr/classic.wav'],
    [false, 'ftp://host.srvr/classic.flac'],
    [false, 'http://host.srvr/something/file.ogg#'],
] as const;

test.each(imageUrls)('Recognizes image files in URLs', (isAudio, urlString) => {
    expect(isImageURL(urlString)).toBe(isAudio);
});
