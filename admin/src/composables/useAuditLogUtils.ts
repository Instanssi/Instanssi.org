import { useI18n } from "vue-i18n";

export interface LoadOptions {
    page: number;
    itemsPerPage: number;
    sortBy: { key: string; order: "asc" | "desc" }[];
}

/**
 * Composable for shared audit log utilities.
 * Provides action label and color mappings for audit log entries.
 */
export function useAuditLogUtils() {
    const { t } = useI18n();

    /**
     * Get a human-readable label for an audit log action.
     * @param action - The action number (0=create, 1=update, 2=delete, 3=access)
     * @param translationPrefix - The translation key prefix (e.g., "AuditLogTable" or "AuditLogView")
     */
    function actionLabel(action: number, translationPrefix: string = "AuditLogTable"): string {
        switch (action) {
            case 0:
                return t(`${translationPrefix}.actions.create`);
            case 1:
                return t(`${translationPrefix}.actions.update`);
            case 2:
                return t(`${translationPrefix}.actions.delete`);
            case 3:
                return t(`${translationPrefix}.actions.access`);
            default:
                return t(`${translationPrefix}.actions.unknown`);
        }
    }

    /**
     * Get a color for an audit log action chip.
     * @param action - The action number (0=create, 1=update, 2=delete, 3=access)
     */
    function actionColor(action: number): string {
        switch (action) {
            case 0:
                return "success";
            case 1:
                return "warning";
            case 2:
                return "error";
            case 3:
                return "info";
            default:
                return "grey";
        }
    }

    return {
        actionLabel,
        actionColor,
    };
}
