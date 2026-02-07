import { computed } from "vue";
import { useDisplay } from "vuetify";
import type { VDataTable } from "vuetify/components";

type Breakpoint = "sm" | "md" | "lg" | "xl";
type ReadonlyHeaders = VDataTable["$props"]["headers"];
type HeaderItem = NonNullable<ReadonlyHeaders>[number];

export type ResponsiveHeader = HeaderItem & {
    minBreakpoint?: Breakpoint;
};

/**
 * Returns a computed headers array that hides columns below their specified breakpoint.
 * Headers without `minBreakpoint` are always shown.
 */
export function useResponsiveHeaders(allHeaders: ResponsiveHeader[]) {
    const display = useDisplay();

    return computed<ReadonlyHeaders>(() =>
        allHeaders.filter((h) => {
            if (!h.minBreakpoint) return true;
            switch (h.minBreakpoint) {
                case "sm":
                    return display.smAndUp.value;
                case "md":
                    return display.mdAndUp.value;
                case "lg":
                    return display.lgAndUp.value;
                case "xl":
                    return display.xlAndUp.value;
            }
        })
    );
}
