import exoFontUrl from "@fontsource/exo/files/exo-latin-700-normal.woff2?url";
import fontkit from "@pdf-lib/fontkit";
import { PDFDocument, rgb, type PDFFont, type PDFPage } from "pdf-lib";

export { toRomanNumeral } from "./roman";

export interface DiplomaOrganizers {
    mainOrganizer: { name: string; title: string };
    programOrganizer: { name: string; title: string };
}

export interface DiplomaData {
    author: string; // Creator name(s)
    entryName: string | null; // Entry name (null for competitions without entries)
    placement: string; // Roman numeral (I, II, III)
    compoName: string; // Competition category name
    eventName: string; // Event name (e.g., "Instanssi 2020")
    hasMultipleAuthors: boolean;
    organizers: DiplomaOrganizers;
}

export interface DiplomaOptions {
    backgroundImageUrl: string;
}

// A4 page dimensions in points (1 point = 0.3528mm)
const PAGE_WIDTH = 595.28; // 210mm
const PAGE_HEIGHT = 841.89; // 297mm

// Colors matching LaTeX template
const INSTANSSI_BLUE = rgb(33 / 255, 60 / 255, 87 / 255);
const INSTANSSI_GREY = rgb(80 / 255, 80 / 255, 80 / 255);
const BLACK = rgb(0, 0, 0);

// Content area: 62.5% of page width (~131mm), centered
const CONTENT_WIDTH = PAGE_WIDTH * 0.625;

/**
 * Detect if an author string represents multiple authors.
 * Checks for common separators: "/", ",", " ja ", " & "
 */
export function hasMultipleAuthors(author: string): boolean {
    return (
        author.includes("/") ||
        author.includes(",") ||
        author.includes(" ja ") ||
        author.includes(" & ")
    );
}

/**
 * Load the Exo font for PDF embedding
 */
async function loadFont(): Promise<ArrayBuffer> {
    const response = await fetch(exoFontUrl);
    if (!response.ok) {
        throw new Error(`Failed to load font: ${response.statusText}`);
    }
    return response.arrayBuffer();
}

/**
 * Load background image from URL and detect its type
 */
async function loadBackgroundImage(
    url: string
): Promise<{ bytes: ArrayBuffer; type: "png" | "jpg" }> {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to load background image: ${response.statusText}`);
    }
    const bytes = await response.arrayBuffer();

    // Detect image type from URL extension or content
    const lowerUrl = url.toLowerCase();
    if (lowerUrl.endsWith(".png")) {
        return { bytes, type: "png" };
    } else if (lowerUrl.endsWith(".jpg") || lowerUrl.endsWith(".jpeg")) {
        return { bytes, type: "jpg" };
    }

    // Try to detect from magic bytes
    const header = new Uint8Array(bytes.slice(0, 8));
    // PNG signature: 137 80 78 71 13 10 26 10
    if (header[0] === 137 && header[1] === 80 && header[2] === 78 && header[3] === 71) {
        return { bytes, type: "png" };
    }
    // JPEG signature: 255 216 255
    if (header[0] === 255 && header[1] === 216 && header[2] === 255) {
        return { bytes, type: "jpg" };
    }

    throw new Error(
        "Unable to detect image type. Please use a PNG or JPEG file with a proper file extension."
    );
}

/**
 * Wrap text to fit within a maximum width, breaking at word boundaries
 */
function wrapText(text: string, font: PDFFont, fontSize: number, maxWidth: number): string[] {
    const words = text.split(" ");
    const lines: string[] = [];
    let currentLine = "";

    for (const word of words) {
        const testLine = currentLine ? `${currentLine} ${word}` : word;
        const testWidth = font.widthOfTextAtSize(testLine, fontSize);

        if (testWidth <= maxWidth) {
            currentLine = testLine;
        } else {
            if (currentLine) {
                lines.push(currentLine);
            }
            currentLine = word;
        }
    }

    if (currentLine) {
        lines.push(currentLine);
    }

    return lines;
}

/**
 * Draw centered text on the page at a given Y position, constrained to content width.
 * If text is too wide, it will be wrapped to multiple lines.
 * Returns the Y position after drawing (accounting for any wrapped lines).
 */
function drawCenteredText(
    page: PDFPage,
    text: string,
    font: PDFFont,
    fontSize: number,
    y: number,
    color: ReturnType<typeof rgb>,
    lineHeight?: number
): number {
    const lines = wrapText(text, font, fontSize, CONTENT_WIDTH);
    const actualLineHeight = lineHeight ?? fontSize + 2;
    let currentY = y;

    for (const line of lines) {
        const textWidth = font.widthOfTextAtSize(line, fontSize);
        const x = (PAGE_WIDTH - textWidth) / 2;
        page.drawText(line, {
            x,
            y: currentY,
            size: fontSize,
            font,
            color,
        });
        currentY -= actualLineHeight;
    }

    return currentY;
}

/**
 * Draw diploma content on a page (text only, background should be drawn first)
 * Layout matching the LaTeX template from DiplomaGenerator
 */
function drawDiplomaContent(page: PDFPage, data: DiplomaData, font: PDFFont): void {
    // Grammar based on single/multiple authors
    const isPlural = data.hasMultipleAuthors;
    const verbIs = isPlural ? "ovat" : "on";
    const verbPlaced = isPlural ? "sijoittuneet" : "sijoittunut";
    const verbDemonstrated = isPlural ? "osoittaneet" : "osoittanut";

    const entryText = `${verbIs} teoksellaan`;
    const eventText = `sijalle ${data.eventName} -tapahtuman kilpasarjassa`;
    const achievementText = `ja täten ${verbDemonstrated} poikkeuksellista osaamista sekä erinomaista taitoa digitaalisen tekemisen saralla.`;

    // Layout positions matching LaTeX template
    // Content starts ~79mm from top (224pt top margin)
    let currentY = PAGE_HEIGHT - 224;

    // 1. Author name (larger size, blue)
    currentY = drawCenteredText(page, data.author, font, 30, currentY, INSTANSSI_BLUE);
    currentY -= 4;

    // 2. "on teoksellaan" / "ovat teoksellaan" (if has entry) - BLACK
    if (data.entryName) {
        currentY = drawCenteredText(page, entryText, font, 12, currentY, BLACK);
        currentY -= 26;

        // 3. Entry name (larger, blue)
        currentY = drawCenteredText(page, data.entryName, font, 30, currentY, INSTANSSI_BLUE);
        currentY -= 2;
    }

    // 4. "sijoittunut" / "sijoittuneet" - BLACK
    currentY = drawCenteredText(page, verbPlaced, font, 12, currentY, BLACK);
    currentY -= 40;

    // 5. Placement I/II/III (large, black)
    currentY = drawCenteredText(page, data.placement, font, 30, currentY, BLACK);
    currentY -= 12;

    // 6. "sijalle {eventName} -tapahtuman kilpasarjassa" - BLACK
    currentY = drawCenteredText(page, eventText, font, 12, currentY, BLACK);
    currentY -= 20;

    // 7. Compo name (larger, black)
    currentY = drawCenteredText(page, data.compoName, font, 18, currentY, BLACK);
    currentY -= 12;

    // 8. Achievement text - BLACK (may wrap to multiple lines)
    currentY = drawCenteredText(page, achievementText, font, 12, currentY, BLACK);

    // Signature section starts ~229mm from top (650pt), independent of content above
    currentY = PAGE_HEIGHT - 650;

    // 9. Organization line (blue)
    currentY = drawCenteredText(
        page,
        "Linkki Jyväskylä ry:n, Hacklab Jyväskylä ry:n ja Instanssin puolesta",
        font,
        10,
        currentY,
        INSTANSSI_BLUE
    );
    currentY -= 40;

    // 10. Signature lines with horizontal rules, names, and titles
    // Signature lines are ~6cm wide (175pt ≈ 62mm)
    const signatureLineWidth = 175;

    // Content margins (same as text content area)
    const contentMargin = (PAGE_WIDTH - CONTENT_WIDTH) / 2;

    // Left signature starts at left content margin
    const leftX = contentMargin;
    // Right signature ends at right content margin
    const rightX = PAGE_WIDTH - contentMargin - signatureLineWidth;

    // Draw horizontal signature rules (lines above names)
    const ruleY = currentY + 14;

    // Left signature line (aligned to left)
    page.drawLine({
        start: { x: leftX, y: ruleY },
        end: { x: leftX + signatureLineWidth, y: ruleY },
        thickness: 1.25,
        color: BLACK,
    });

    // Right signature line (aligned to right)
    page.drawLine({
        start: { x: rightX, y: ruleY },
        end: { x: rightX + signatureLineWidth, y: ruleY },
        thickness: 1.25,
        color: BLACK,
    });

    // Left signature (main organizer) - left-aligned under the line
    if (data.organizers.mainOrganizer.name) {
        page.drawText(data.organizers.mainOrganizer.name, {
            x: leftX,
            y: currentY,
            size: 10,
            font,
            color: BLACK,
        });
        page.drawText(data.organizers.mainOrganizer.title, {
            x: leftX,
            y: currentY - 12,
            size: 10,
            font,
            color: INSTANSSI_GREY,
        });
    }

    // Right signature (program organizer) - right-aligned under the line
    if (data.organizers.programOrganizer.name) {
        const nameWidth = font.widthOfTextAtSize(data.organizers.programOrganizer.name, 10);
        const titleWidth = font.widthOfTextAtSize(data.organizers.programOrganizer.title, 10);
        page.drawText(data.organizers.programOrganizer.name, {
            x: rightX + signatureLineWidth - nameWidth,
            y: currentY,
            size: 10,
            font,
            color: BLACK,
        });
        page.drawText(data.organizers.programOrganizer.title, {
            x: rightX + signatureLineWidth - titleWidth,
            y: currentY - 12,
            size: 10,
            font,
            color: INSTANSSI_GREY,
        });
    }
}

/**
 * Progress callback type for diploma generation
 */
export type DiplomaProgressCallback = (current: number, total: number) => void;

/**
 * Generate a single multi-page PDF containing all diplomas
 * @param diplomas - Array of diploma data to generate
 * @param options - Generation options including background image URL
 * @param onProgress - Optional callback to report generation progress
 */
export async function generateAllDiplomasPdf(
    diplomas: DiplomaData[],
    options: DiplomaOptions,
    onProgress?: DiplomaProgressCallback
): Promise<Uint8Array> {
    if (diplomas.length === 0) {
        throw new Error("No diplomas to generate");
    }

    const total = diplomas.length;

    // Create PDF document
    const pdfDoc = await PDFDocument.create();
    pdfDoc.registerFontkit(fontkit);

    // Load font once
    // Disable ligatures to prevent "ff", "fi", "fl" etc. from disappearing in PDFs
    const fontBytes = await loadFont();
    const font = await pdfDoc.embedFont(fontBytes, { features: { liga: false } });

    // Load and embed background image once
    const { bytes: imgBytes, type: imgType } = await loadBackgroundImage(
        options.backgroundImageUrl
    );
    const image =
        imgType === "png" ? await pdfDoc.embedPng(imgBytes) : await pdfDoc.embedJpg(imgBytes);

    // Generate a page for each diploma
    for (const [i, data] of diplomas.entries()) {
        const page = pdfDoc.addPage([PAGE_WIDTH, PAGE_HEIGHT]);

        // Draw background image
        page.drawImage(image, {
            x: 0,
            y: 0,
            width: PAGE_WIDTH,
            height: PAGE_HEIGHT,
        });

        // Draw diploma content
        drawDiplomaContent(page, data, font);

        // Report progress
        onProgress?.(i + 1, total);
    }

    return pdfDoc.save();
}
