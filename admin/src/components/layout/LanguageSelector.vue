<template>
    <v-menu>
        <template #activator="{ props }">
            <v-btn v-bind="props" variant="text" size="small">
                <template #prepend>
                    <FontAwesomeIcon :icon="faLanguage" />
                </template>
                {{ LOCALE_NAMES[locale as SupportedLocale] ?? locale }}
            </v-btn>
        </template>
        <v-list density="compact">
            <v-list-item
                v-for="loc in SUPPORTED_LOCALES"
                :key="loc"
                :active="locale === loc"
                @click="selectLocale(loc)"
            >
                <v-list-item-title>{{ LOCALE_NAMES[loc] }}</v-list-item-title>
            </v-list-item>
        </v-list>
    </v-menu>
</template>

<script setup lang="ts">
import { faLanguage } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { useI18n } from "vue-i18n";

import { LOCALE_NAMES, SUPPORTED_LOCALES, type SupportedLocale } from "@/i18n";
import { useAuth } from "@/services/auth";

const { locale } = useI18n();
const authService = useAuth();

function selectLocale(loc: SupportedLocale): void {
    authService.updateLanguage(loc);
}
</script>
