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
                        :href="method.url"
                    >
                        <template v-if="socialIcons[method.method]" #prepend>
                            <FontAwesomeIcon :icon="socialIcons[method.method]!" />
                        </template>
                        {{ method.name }}
                    </v-btn>
                </div>
                <v-form class="mt-4" @submit.prevent="submit">
                    <v-container class="ma-0 pa-0">
                        <v-row dense no-gutters class="mb-2 mt-2">
                            <v-text-field
                                v-model="email.value.value"
                                :error-messages="email.errorMessage.value"
                                density="compact"
                                variant="outlined"
                                :label="t('LoginView.email')"
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
                        <v-row dense no-gutters class="justify-space-between align-center">
                            <LanguageSelector />
                            <v-btn type="submit" color="primary" variant="elevated">
                                <template #prepend>
                                    <FontAwesomeIcon :icon="faRightToBracket" />
                                </template>
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
import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { faGithub, faGoogle } from "@fortawesome/free-brands-svg-icons";
import { faRightToBracket } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { useField, useForm } from "vee-validate";
import { type Ref, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { object as yupObject, string as yupString } from "yup";

import type { SocialAuthUrl } from "@/api";
import LanguageSelector from "@/components/layout/LanguageSelector.vue";
import { PermissionTarget, useAuth } from "@/services/auth";

const authService = useAuth();
const router = useRouter();
const { t } = useI18n();

const socialIcons: Record<string, IconDefinition> = {
    google: faGoogle,
    github: faGithub,
};

const socialLoginUrls: Ref<SocialAuthUrl[]> = ref([]);

// Field validation rules
const validationSchema = yupObject({
    email: yupString().required().min(1),
    password: yupString().required().min(1),
});
const { handleSubmit, setErrors } = useForm({ validationSchema });
const email = useField("email");
const password = useField("password");

const submit = handleSubmit(async (values) => {
    const loginOk = await authService.login(values.email, values.password);
    if (!loginOk) {
        setErrors({
            email: t("LoginView.auth_failed"),
            password: t("LoginView.auth_failed"),
        });
        return;
    }
    if (!authService.canView(PermissionTarget.EVENT)) {
        await authService.logout();
        setErrors({
            email: t("LoginView.insufficient_permissions"),
            password: t("LoginView.insufficient_permissions"),
        });
        return;
    }
    await router.push({ name: "index" });
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
