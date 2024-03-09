<template>
    <div class="d-flex align-center justify-center fill-height bg-grey-darken-3">
        <v-card color="grey-darken-4" title="Sign in">
            <template v-slot:subtitle>
                Sign in using username and password, or by using one of the SSO methods.
            </template>
            <template v-slot:text>
                <v-form>
                    <v-container class="ma-0 pa-0">
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
                </v-form>
            </template>
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

<style scoped lang="scss">
</style>
