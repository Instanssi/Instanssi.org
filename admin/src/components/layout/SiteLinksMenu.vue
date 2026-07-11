<template>
    <v-menu>
        <template #activator="{ props: activatorProps }">
            <v-btn v-bind="activatorProps" variant="text" icon>
                <FontAwesomeIcon :icon="faGlobe" />
            </v-btn>
        </template>
        <v-list density="compact">
            <v-list-item
                v-for="link in SITE_LINKS"
                :key="link.href"
                :href="link.href"
                :title="t(link.titleKey)"
            />
        </v-list>
    </v-menu>
</template>

<script setup lang="ts">
import { faGlobe } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { useI18n } from "vue-i18n";

import { SITE_LINKS } from "@/components/layout/siteLinks";

const { t } = useI18n();
</script>
