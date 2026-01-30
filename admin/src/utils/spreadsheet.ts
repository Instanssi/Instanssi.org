import * as XLSX from "xlsx";

export type SpreadsheetFormat = "csv" | "xlsx" | "ods";

/**
 * Get file extension and MIME type for a format
 */
function getFormatInfo(format: SpreadsheetFormat): { extension: string; mimeType: string } {
    switch (format) {
        case "xlsx":
            return {
                extension: "xlsx",
                mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            };
        case "ods":
            return { extension: "ods", mimeType: "application/vnd.oasis.opendocument.spreadsheet" };
        case "csv":
        default:
            return { extension: "csv", mimeType: "text/csv;charset=utf-8" };
    }
}

/**
 * Download data as a spreadsheet file.
 * @param data - Array of rows, where each row is an array of cell values
 * @param filename - Base filename without extension
 * @param format - Output format (csv, xlsx, ods)
 * @param sheetName - Name of the worksheet (default: "Sheet1")
 */
export function downloadSpreadsheet(
    data: Array<Array<string | number>>,
    filename: string,
    format: SpreadsheetFormat = "csv",
    sheetName: string = "Sheet1"
): void {
    const worksheet = XLSX.utils.aoa_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);

    const { extension, mimeType } = getFormatInfo(format);
    const fullFilename = `${filename}.${extension}`;

    // Generate file content
    const content = XLSX.write(workbook, {
        bookType: format === "ods" ? "ods" : format === "xlsx" ? "xlsx" : "csv",
        type: "array",
    });

    // Trigger download
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fullFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}
