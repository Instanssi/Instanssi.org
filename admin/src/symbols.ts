import type { InjectionKey, Ref } from "vue";
import type ConfirmDialog from "@/components/ConfirmDialog.vue";

export type ConfirmDialogType = Ref<undefined | InstanceType<typeof ConfirmDialog>>;

export const confirmDialogKey = Symbol() as InjectionKey<ConfirmDialogType>;
