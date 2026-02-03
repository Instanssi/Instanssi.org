/**
 * Lookup table for Roman numeral conversion.
 * Organized in groups of 10: hundreds (0-9), tens (10-19), ones (20-29)
 */
const NUMERAL_KEYS = [
    "",
    "C",
    "CC",
    "CCC",
    "CD",
    "D",
    "DC",
    "DCC",
    "DCCC",
    "CM",
    "",
    "X",
    "XX",
    "XXX",
    "XL",
    "L",
    "LX",
    "LXX",
    "LXXX",
    "XC",
    "",
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
];

/**
 * Convert a number to Roman numerals.
 * Supports values from 0 to 3999 (standard Roman numeral range).
 * @param num - The number to convert
 * @returns Roman numeral string (e.g., 1 → "I", 4 → "IV", 1987 → "MCMLXXXVII")
 */
export function toRomanNumeral(num: number): string {
    if (isNaN(num)) return String(NaN);
    const digits = String(+num).split("");
    let roman = "";
    let i = 3;
    while (i--) {
        const digit = digits.pop() ?? "0";
        roman = (NUMERAL_KEYS[+digit + i * 10] || "") + roman;
    }
    return Array(+digits.join("") + 1).join("M") + roman;
}
