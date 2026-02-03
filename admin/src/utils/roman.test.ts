import { describe, expect, it } from "vitest";

import { toRomanNumeral } from "./roman";

describe("toRomanNumeral", () => {
    it("converts 1-3 correctly", () => {
        expect(toRomanNumeral(1)).toBe("I");
        expect(toRomanNumeral(2)).toBe("II");
        expect(toRomanNumeral(3)).toBe("III");
    });

    it("converts 4 and 9 using subtractive notation", () => {
        expect(toRomanNumeral(4)).toBe("IV");
        expect(toRomanNumeral(9)).toBe("IX");
    });

    it("converts 5-8 correctly", () => {
        expect(toRomanNumeral(5)).toBe("V");
        expect(toRomanNumeral(6)).toBe("VI");
        expect(toRomanNumeral(7)).toBe("VII");
        expect(toRomanNumeral(8)).toBe("VIII");
    });

    it("converts 10-39 correctly", () => {
        expect(toRomanNumeral(10)).toBe("X");
        expect(toRomanNumeral(14)).toBe("XIV");
        expect(toRomanNumeral(19)).toBe("XIX");
        expect(toRomanNumeral(20)).toBe("XX");
        expect(toRomanNumeral(30)).toBe("XXX");
    });

    it("converts 40 and 90 using subtractive notation", () => {
        expect(toRomanNumeral(40)).toBe("XL");
        expect(toRomanNumeral(90)).toBe("XC");
    });

    it("converts 50-89 correctly", () => {
        expect(toRomanNumeral(50)).toBe("L");
        expect(toRomanNumeral(60)).toBe("LX");
        expect(toRomanNumeral(70)).toBe("LXX");
        expect(toRomanNumeral(80)).toBe("LXXX");
    });

    it("converts 100-399 correctly", () => {
        expect(toRomanNumeral(100)).toBe("C");
        expect(toRomanNumeral(200)).toBe("CC");
        expect(toRomanNumeral(300)).toBe("CCC");
    });

    it("converts 400 and 900 using subtractive notation", () => {
        expect(toRomanNumeral(400)).toBe("CD");
        expect(toRomanNumeral(900)).toBe("CM");
    });

    it("converts 500-899 correctly", () => {
        expect(toRomanNumeral(500)).toBe("D");
        expect(toRomanNumeral(600)).toBe("DC");
        expect(toRomanNumeral(700)).toBe("DCC");
        expect(toRomanNumeral(800)).toBe("DCCC");
    });

    it("converts 1000+ using M", () => {
        expect(toRomanNumeral(1000)).toBe("M");
        expect(toRomanNumeral(2000)).toBe("MM");
        expect(toRomanNumeral(3000)).toBe("MMM");
    });

    it("converts complex numbers correctly", () => {
        expect(toRomanNumeral(1987)).toBe("MCMLXXXVII");
        expect(toRomanNumeral(2024)).toBe("MMXXIV");
        expect(toRomanNumeral(1999)).toBe("MCMXCIX");
        expect(toRomanNumeral(444)).toBe("CDXLIV");
    });

    it("handles edge cases", () => {
        expect(toRomanNumeral(0)).toBe("");
        expect(toRomanNumeral(NaN)).toBe("NaN");
    });
});
