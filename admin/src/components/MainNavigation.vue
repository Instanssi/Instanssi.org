<template>
    <v-navigation-drawer color="grey-darken-4">
        <div class="d-flex ma-5 align-center">
            <v-img src="@/assets/icon.png" />
            <h1 class="pl-2">Instanssi</h1>
        </div>
        <v-divider></v-divider>
        <v-list density="compact" open-strategy="multiple" nav>
            <template v-for="item in items">
                <v-list-group v-if="item.children" :key="`group-${item.title}`">
                    <template v-slot:activator="{ props }">
                        <v-list-item
                            v-bind="props"
                            :prepend-icon="item.icon"
                            :title="item.title"
                        />
                    </template>
                    <v-list-item
                        v-for="child in item.children"
                        :key="`${item.title}-${child.title}`"
                        :prepend-icon="child.icon"
                        :title="child.title"
                        @click="navigateTo(child.to)"
                    />
                </v-list-group>
                <v-list-item
                    v-else
                    :key="`root-${item.title}`"
                    :prepend-icon="item.icon"
                    :title="item.title"
                    @click="navigateTo(item.to)"
                />
            </template>
        </v-list>
    </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

export type NavigationLink = {
    title: string
    icon: string
    to?: string
    children?: NavigationLink[]
};
export type NavigationLinks = NavigationLink[];

const router = useRouter();

defineProps<{items: NavigationLinks}>();

function navigateTo(to: string|undefined): void {
    if (!to) return;
    router.push({name: to});
}
</script>

<style scoped>
h1 {
    font-size: 1.9em;
    text-transform: uppercase;
}
</style>
