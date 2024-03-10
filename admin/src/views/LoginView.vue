<template>
    <div class="d-flex align-center justify-center fill-height bg-grey-darken-3">
        <v-card color="grey-darken-4" title="Sign in">
            <template v-slot:subtitle>
                Sign in using username and password, or by using one of the SSO methods.
            </template>
            <template v-slot:text>
                <div class="d-flex justify-center">
                    <v-btn
                        v-for="method in socialLoginUrls"
                        :key="method.method"
                        variant="plain"
                        :prepend-icon="`fab fa-${method.method}`"
                        :href="method.url"
                        >{{ method.name }}</v-btn
                    >
                </div>
                <v-form class="mt-4" @submit.prevent="submit">
                    <v-container class="ma-0 pa-0">
                        <v-row dense no-gutters class="mb-2 mt-2">
                            <v-text-field
                                v-model="username.value.value"
                                :error-messages="username.errorMessage.value"
                                density="compact"
                                variant="outlined"
                                label="Username"
                            />
                        </v-row>
                        <v-row dense no-gutters class="mb-2 mt-2">
                            <v-text-field
                                v-model="password.value.value"
                                :error-messages="password.errorMessage.value"
                                density="compact"
                                variant="outlined"
                                label="Password"
                            />
                        </v-row>
                        <v-row dense no-gutters class="justify-end">
                            <v-btn
                                type="submit"
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
import { onMounted, type Ref, ref } from "vue";
import { object as yupObject, string as yupString } from "yup";

import { useAuth } from "@/services/auth";
import { useRouter } from "vue-router";
import type { SocialAuthUrls } from "@/apis/types";
import { useField, useForm } from "vee-validate";

const authService = useAuth();
const router = useRouter();

const socialLoginUrls: Ref<SocialAuthUrls> = ref([]);

// Field validation rules
const validationSchema = yupObject({
    username: yupString().required().min(1),
    password: yupString().required().min(1),
});
const { handleSubmit, setErrors } = useForm({ validationSchema });
const username = useField("username");
const password = useField("password");

const submit = handleSubmit(async (values) => {
    const loginOk = await authService.login(values.username, values.password);
    if (loginOk) {
        await router.push({ name: "dashboard" });
    } else {
        setErrors({
            username: "Incorrect username or password!",
            password: "Incorrect username or password!",
        });
    }
});

onMounted(async () => {
    socialLoginUrls.value = await authService.getSocialAuthURLs();
});
</script>

<style scoped lang="scss"></style>
