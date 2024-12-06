<template>
    <div class="d-flex align-center justify-center fill-height">
        <v-card color="grey-darken-4" class="opacity-95" :title="t('LoginView.title')">
            <template #subtitle>
                {{ t("LoginView.subtitle") }}
            </template>
            <template #text>
                <div class="d-flex justify-center">
                    <v-btn
                        v-for="method in socialLoginUrls"
                        :key="method.method"
                        variant="plain"
                        :prepend-icon="`fab fa-${method.method}`"
                        :href="method.url"
                    >
                        {{ method.name }}
                    </v-btn>
                </div>
                <v-form class="mt-4" @submit.prevent="submit">
                    <v-container class="ma-0 pa-0">
                        <v-row dense no-gutters class="mb-2 mt-2">
                            <v-text-field
                                v-model="username.value.value"
                                :error-messages="username.errorMessage.value"
                                density="compact"
                                variant="outlined"
                                :label="t('LoginView.username')"
                            />
                        </v-row>
                        <v-row dense no-gutters class="mb-2 mt-2">
                            <v-text-field
                                v-model="password.value.value"
                                :error-messages="password.errorMessage.value"
                                type="password"
                                density="compact"
                                variant="outlined"
                                :label="t('LoginView.password')"
                            />
                        </v-row>
                        <v-row dense no-gutters class="justify-end">
                            <v-btn
                                type="submit"
                                color="primary"
                                variant="elevated"
                                prepend-icon="fas fa-right-to-bracket"
                            >
                                {{ t("LoginView.login") }}
                            </v-btn>
                        </v-row>
                    </v-container>
                </v-form>
            </template>
        </v-card>
    </div>
</template>

<script setup lang="ts">
import { useField, useForm } from "vee-validate";
import { type Ref, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { object as yupObject, string as yupString } from "yup";

import type { SocialAuthURL } from "@/api";
import { useAuth } from "@/services/auth";

const authService = useAuth();
const router = useRouter();
const { t } = useI18n();

const socialLoginUrls: Ref<SocialAuthURL[]> = ref([]);

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
        await router.push({ name: "index" });
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

<style scoped lang="scss">
.opacity-95 {
    opacity: 0.95;
}
</style>
