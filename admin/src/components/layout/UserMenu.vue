<template>
    <v-menu>
        <template #activator="{ props: activatorProps }">
            <v-btn v-bind="activatorProps" variant="text">
                <FontAwesomeIcon :icon="faUser" />
                <span v-if="displayName" class="ml-2 d-none d-sm-inline">{{ displayName }}</span>
            </v-btn>
        </template>
        <v-list density="compact">
            <v-list-item href="/users/profile/" :title="t('UserMenu.profile')" />
            <v-list-item href="/users/email/" :title="t('UserMenu.emailAddresses')" />
            <v-list-item href="/users/password/change/" :title="t('UserMenu.changePassword')" />
            <v-list-item href="/users/3rdparty/" :title="t('UserMenu.connectedAccounts')" />
            <v-list-item
                :title="t('UserMenu.notifications')"
                @click="router.push({ name: 'notifications' })"
            />
            <v-divider />
            <v-list-item :title="t('UserMenu.logout')" @click="router.push({ name: 'logout' })" />
        </v-list>
    </v-menu>
</template>

<script setup lang="ts">
import { faUser } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

import { useAuth } from "@/services/auth";

const { t } = useI18n();
const router = useRouter();
const { userInfo } = useAuth();

const displayName = computed(() => userInfo.value.email || userInfo.value.username);
</script>
