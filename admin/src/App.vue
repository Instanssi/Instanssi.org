<template>
    <v-app>
        <v-navigation-drawer color="grey-darken-4">
            <div class="d-flex ma-5 align-center">
                <v-img src="@/assets/icon.png" />
                <h1 class="pl-2">Instanssi</h1>
            </div>

            <v-divider></v-divider>

            <v-list density="compact" nav>
                <v-list-item prepend-icon="fas fa-dashboard" title="Dashboard" value="dashboard" />
                <v-list-item prepend-icon="fas fa-right-from-bracket" title="Log out" value="logout" />
            </v-list>
        </v-navigation-drawer>
        <v-main>
            <RouterView />
        </v-main>
    </v-app>
</template>

<script setup lang="ts"></script>

<style scoped>
h1 {
    font-size: 1.9em;
    text-transform: uppercase;
}
</style>
