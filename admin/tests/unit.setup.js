import { vi } from "vitest";
import { config } from '@vue/test-utils';
import { useI18n } from "vue-i18n";
import { createVuetify } from "vuetify";

vi.mock("vue-i18n");

useI18n.mockReturnValue({
    t: (tKey) => tKey,
    d: (dKey) => dKey,
});

config.global.plugins = [createVuetify()]
