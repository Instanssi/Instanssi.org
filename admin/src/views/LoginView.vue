<template>
    <div class="d-flex align-center justify-center fill-height bg-grey-darken-3">
        <v-card min-width="500" color="grey-darken-4">
            <v-card-title class="ml-4 mr-4 headline text-truncate">
                <v-icon icon="fas fa-lock" size="x-small" />
                <span class="ml-3">Login</span>
            </v-card-title>
            <v-card-text>
                <v-container fluid>
                    <v-row dense no-gutters>
                        <v-text-field
                            density="compact"
                            variant="outlined"
                            label="Username"
                            model="username"
                        />
                    </v-row>
                    <v-row dense no-gutters>
                        <v-text-field
                            density="compact"
                            variant="outlined"
                            label="Password"
                            model="password"
                        />
                    </v-row>
                    <v-row dense no-gutters class="justify-end">
                        <v-btn
                            @click="login"
                            color="primary"
                            variant="elevated"
                            prepend-icon="fas fa-right-to-bracket"
                            >Login</v-btn
                        >
                    </v-row>
                </v-container>
            </v-card-text>
        </v-card>
    </div>
</template>

<script setup lang="ts">
import { useAuth } from "@/services/auth";
import { useRouter } from "vue-router";
import { ref } from "vue";

const authService = useAuth();
const router = useRouter();
const username = ref("");
const password = ref("");

async function login() {
    const loginOk = await authService.login(username.value, password.value);
    if (loginOk) {
        await router.push({ name: "dashboard" });
    }
}
</script>

<style scoped lang="scss"></style>
