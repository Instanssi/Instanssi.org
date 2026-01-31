<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <v-card>
                <v-card-text>
                    <v-form @submit.prevent="submit">
                        <FormSection>
                            {{ t("StoreItemEditView.sections.basicInfo") }}
                        </FormSection>
                        <v-text-field
                            v-model="name.value.value"
                            :error-messages="name.errorMessage.value"
                            variant="outlined"
                            :label="t('StoreItemEditView.labels.name') + ' *'"
                        />
                        <VuetifyTiptap v-model="description.value.value" />
                        <div
                            v-if="description.errorMessage.value"
                            class="text-error text-caption mb-4"
                        >
                            {{ description.errorMessage.value }}
                        </div>

                        <FormSection>
                            {{ t("StoreItemEditView.sections.image") }}
                        </FormSection>
                        <v-file-input
                            v-model="imageFile.value.value"
                            :label="t('StoreItemEditView.labels.imagefile')"
                            :error-messages="imageFile.errorMessage.value"
                            variant="outlined"
                            accept="image/*"
                            prepend-icon=""
                            clearable
                        >
                            <template #prepend>
                                <FontAwesomeIcon :icon="faImage" />
                            </template>
                        </v-file-input>
                        <v-img
                            v-if="currentImageUrl"
                            :src="currentImageUrl"
                            max-width="200"
                            class="mb-4"
                        />

                        <FormSection>
                            {{ t("StoreItemEditView.sections.pricing") }}
                        </FormSection>
                        <v-row>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model="price.value.value"
                                    :error-messages="price.errorMessage.value"
                                    variant="outlined"
                                    :label="t('StoreItemEditView.labels.price') + ' *'"
                                    type="number"
                                    step="0.01"
                                    min="0"
                                    suffix="EUR"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model.number="discountAmount.value.value"
                                    :error-messages="discountAmount.errorMessage.value"
                                    variant="outlined"
                                    :label="t('StoreItemEditView.labels.discountAmount')"
                                    type="number"
                                    min="-1"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model.number="discountPercentage.value.value"
                                    :error-messages="discountPercentage.errorMessage.value"
                                    variant="outlined"
                                    :label="t('StoreItemEditView.labels.discountPercentage')"
                                    type="number"
                                    min="0"
                                    max="100"
                                    suffix="%"
                                />
                            </v-col>
                        </v-row>

                        <FormSection>
                            {{ t("StoreItemEditView.sections.availability") }}
                        </FormSection>
                        <v-row>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model.number="max.value.value"
                                    :error-messages="max.errorMessage.value"
                                    variant="outlined"
                                    :label="t('StoreItemEditView.labels.max') + ' *'"
                                    type="number"
                                    min="0"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model.number="maxPerOrder.value.value"
                                    :error-messages="maxPerOrder.errorMessage.value"
                                    variant="outlined"
                                    :label="t('StoreItemEditView.labels.maxPerOrder')"
                                    type="number"
                                    min="1"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model.number="sortIndex.value.value"
                                    :error-messages="sortIndex.errorMessage.value"
                                    variant="outlined"
                                    :label="t('StoreItemEditView.labels.sortIndex')"
                                    type="number"
                                />
                            </v-col>
                        </v-row>

                        <FormSection>
                            {{ t("StoreItemEditView.sections.visibility") }}
                        </FormSection>
                        <ToggleSwitch
                            v-model="available.value.value"
                            :error-message="available.errorMessage.value"
                            :label-on="t('StoreItemEditView.labels.availableOn')"
                            :label-off="t('StoreItemEditView.labels.availableOff')"
                            :hint-on="t('StoreItemEditView.labels.availableHintOn')"
                            :hint-off="t('StoreItemEditView.labels.availableHintOff')"
                        />
                        <ToggleSwitch
                            v-model="isTicket.value.value"
                            :error-message="isTicket.errorMessage.value"
                            :label-on="t('StoreItemEditView.labels.isTicketOn')"
                            :label-off="t('StoreItemEditView.labels.isTicketOff')"
                            :hint-on="t('StoreItemEditView.labels.isTicketHintOn')"
                            :hint-off="t('StoreItemEditView.labels.isTicketHintOff')"
                        />
                        <v-row align="center">
                            <v-col cols="12" :md="isSecret.value.value ? 6 : 12">
                                <ToggleSwitch
                                    v-model="isSecret.value.value"
                                    :error-message="isSecret.errorMessage.value"
                                    :label-on="t('StoreItemEditView.labels.isSecretOn')"
                                    :label-off="t('StoreItemEditView.labels.isSecretOff')"
                                    :hint-on="t('StoreItemEditView.labels.isSecretHintOn')"
                                    :hint-off="t('StoreItemEditView.labels.isSecretHintOff')"
                                />
                            </v-col>
                            <v-col v-if="isSecret.value.value" cols="12" md="6">
                                <v-text-field
                                    v-model="secretKey.value.value"
                                    :error-messages="secretKey.errorMessage.value"
                                    variant="outlined"
                                    :label="t('StoreItemEditView.labels.secretKey')"
                                    hide-details="auto"
                                />
                            </v-col>
                        </v-row>

                        <!-- Variants section (only in edit mode) -->
                        <template v-if="isEditMode">
                            <FormSection>
                                {{ t("StoreItemEditView.sections.variants") }}
                            </FormSection>
                            <v-card variant="outlined" class="mb-4">
                                <v-card-text>
                                    <v-list v-if="variants.length > 0" density="compact">
                                        <v-list-item v-for="variant in variants" :key="variant.id">
                                            <v-list-item-title>{{
                                                variant.name
                                            }}</v-list-item-title>
                                            <template #append>
                                                <v-btn
                                                    v-if="
                                                        auth.canDelete(
                                                            PermissionTarget.STORE_ITEM_VARIANT
                                                        )
                                                    "
                                                    icon
                                                    variant="text"
                                                    color="red"
                                                    size="small"
                                                    @click="deleteVariant(variant)"
                                                >
                                                    <FontAwesomeIcon :icon="faXmark" />
                                                </v-btn>
                                            </template>
                                        </v-list-item>
                                    </v-list>
                                    <div v-else class="text-grey text-body-2 mb-4">
                                        {{ t("StoreItemEditView.variants.noVariants") }}
                                    </div>
                                    <v-row
                                        v-if="auth.canAdd(PermissionTarget.STORE_ITEM_VARIANT)"
                                        align="center"
                                        class="mt-2"
                                    >
                                        <v-col cols="auto" class="flex-grow-1">
                                            <v-text-field
                                                v-model="newVariantName"
                                                variant="outlined"
                                                density="compact"
                                                :label="t('StoreItemEditView.variants.name')"
                                                hide-details
                                            />
                                        </v-col>
                                        <v-col cols="auto">
                                            <v-btn
                                                color="primary"
                                                :disabled="!newVariantName.trim()"
                                                :loading="variantSaving"
                                                @click="addVariant"
                                            >
                                                <template #prepend>
                                                    <FontAwesomeIcon :icon="faPlus" />
                                                </template>
                                                {{ t("StoreItemEditView.variants.addVariant") }}
                                            </v-btn>
                                        </v-col>
                                    </v-row>
                                </v-card-text>
                            </v-card>
                        </template>
                    </v-form>
                </v-card-text>
                <v-card-actions class="justify-end">
                    <v-btn variant="text" @click="goBack">
                        {{ t("General.cancel") }}
                    </v-btn>
                    <v-btn
                        variant="elevated"
                        color="primary"
                        :loading="saving"
                        :disabled="!meta.valid"
                        @click="submit"
                    >
                        <template #prepend>
                            <FontAwesomeIcon :icon="faSave" />
                        </template>
                        {{ t("General.save") }}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-col>
    </LayoutBase>
</template>

<script setup lang="ts">
import {
    faFloppyDisk as faSave,
    faImage,
    faPlus,
    faXmark,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { parseInt } from "lodash-es";
import { type GenericObject, useField, useForm } from "vee-validate";
import { computed, inject, onMounted, ref, type Ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import {
    boolean as yupBoolean,
    mixed as yupMixed,
    number as yupNumber,
    object as yupObject,
    string as yupString,
} from "yup";

import * as api from "@/api";
import type { StoreItemVariant } from "@/api";
import FormSection from "@/components/form/FormSection.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/layout/LayoutBase.vue";
import ToggleSwitch from "@/components/form/ToggleSwitch.vue";
import { PermissionTarget, useAuth } from "@/services/auth";
import { useEvents } from "@/services/events";
import { confirmDialogKey } from "@/symbols";
import type { ConfirmDialogType } from "@/symbols";
import { type FileValue, getFile } from "@/utils/file";
import { getApiErrorMessage, handleApiError } from "@/utils/http";

const props = defineProps<{
    eventId: string;
    id?: string;
}>();

const { t } = useI18n();
const router = useRouter();
const toast = useToast();
const { getEventById } = useEvents();
const auth = useAuth();
const confirmDialog: ConfirmDialogType = inject(confirmDialogKey)!;

const loading = ref(false);
const saving = ref(false);
const variantSaving = ref(false);
const itemName = ref<string>("");
const eventId = computed(() => parseInt(props.eventId, 10));
const isEditMode = computed(() => props.id !== undefined);
const currentImageUrl = ref<string | null>(null);
const variants: Ref<StoreItemVariant[]> = ref([]);
const newVariantName = ref("");

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = [
        {
            title: getEventById(eventId.value)?.name ?? "...",
            to: { name: "dashboard", params: { eventId: props.eventId } },
        },
        {
            title: t("StoreItemsView.title"),
            to: { name: "store-items", params: { eventId: props.eventId } },
        },
    ];
    if (isEditMode.value) {
        items.push({ title: itemName.value || "...", disabled: true });
    } else {
        items.push({ title: t("Breadcrumbs.newStoreItem"), disabled: true });
    }
    return items;
});

// Form validation
const validationSchema = yupObject({
    name: yupString().required().min(1).max(255),
    description: yupString(),
    price: yupString().required(),
    max: yupNumber().required().min(0),
    maxPerOrder: yupNumber().nullable().min(1),
    sortIndex: yupNumber().nullable(),
    discountAmount: yupNumber().nullable().min(-1),
    discountPercentage: yupNumber().nullable().min(0).max(100),
    available: yupBoolean(),
    isTicket: yupBoolean(),
    isSecret: yupBoolean(),
    secretKey: yupString(),
    imageFile: yupMixed().nullable(),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        name: "",
        description: "",
        price: "0.00",
        max: 0,
        maxPerOrder: null as number | null,
        sortIndex: 0,
        discountAmount: -1,
        discountPercentage: 0,
        available: true,
        isTicket: false,
        isSecret: false,
        secretKey: "",
        imageFile: null as FileValue,
    },
});

const name = useField<string>("name");
const description = useField<string>("description");
const price = useField<string>("price");
const max = useField<number>("max");
const maxPerOrder = useField<number | null>("maxPerOrder");
const sortIndex = useField<number>("sortIndex");
const discountAmount = useField<number>("discountAmount");
const discountPercentage = useField<number>("discountPercentage");
const available = useField<boolean>("available");
const isTicket = useField<boolean>("isTicket");
const isSecret = useField<boolean>("isSecret");
const secretKey = useField<string>("secretKey");
const imageFile = useField<FileValue>("imageFile");

const submit = handleSubmit(async (values) => {
    saving.value = true;
    let ok: boolean;
    if (isEditMode.value) {
        ok = await editItem(parseInt(props.id!, 10), values);
    } else {
        ok = await createItem(values);
    }
    saving.value = false;
    if (ok) {
        goBack();
    }
});

async function createItem(values: GenericObject) {
    try {
        // Always use FormData for this endpoint (supports optional file uploads)
        await api.adminEventStoreItemsCreate({
            path: { event_pk: eventId.value },
            body: {
                name: values.name,
                description: values.description || "",
                price: values.price,
                max: values.max,
                max_per_order: values.maxPerOrder ?? undefined,
                sort_index: values.sortIndex ?? 0,
                discount_amount: values.discountAmount ?? -1,
                discount_percentage: values.discountPercentage ?? 0,
                available: values.available,
                is_ticket: values.isTicket,
                is_secret: values.isSecret,
                secret_key: values.secretKey || undefined,
                imagefile_original: getFile(values.imageFile),
            },
            bodySerializer: (body) => {
                const formData = new FormData();
                formData.append("name", body.name);
                formData.append("description", body.description || "");
                formData.append("price", body.price);
                formData.append("max", String(body.max));
                if (body.max_per_order !== undefined)
                    formData.append("max_per_order", String(body.max_per_order));
                formData.append("sort_index", String(body.sort_index ?? 0));
                formData.append("discount_amount", String(body.discount_amount ?? -1));
                formData.append("discount_percentage", String(body.discount_percentage ?? 0));
                formData.append("available", body.available ? "true" : "false");
                formData.append("is_ticket", body.is_ticket ? "true" : "false");
                formData.append("is_secret", body.is_secret ? "true" : "false");
                if (body.secret_key) formData.append("secret_key", body.secret_key);
                if (body.imagefile_original)
                    formData.append("imagefile_original", body.imagefile_original);
                return formData;
            },
        });
        toast.success(t("StoreItemEditView.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("StoreItemEditView.createFailure"), {
            name: "name",
            description: "description",
            price: "price",
            max: "max",
            max_per_order: "maxPerOrder",
            sort_index: "sortIndex",
            discount_amount: "discountAmount",
            discount_percentage: "discountPercentage",
            available: "available",
            is_ticket: "isTicket",
            is_secret: "isSecret",
            secret_key: "secretKey",
            imagefile_original: "imageFile",
        });
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    try {
        // Always use FormData for this endpoint (supports optional file uploads)
        await api.adminEventStoreItemsPartialUpdate({
            path: { event_pk: eventId.value, id: itemId },
            body: {
                name: values.name,
                description: values.description || "",
                price: values.price,
                max: values.max,
                max_per_order: values.maxPerOrder ?? undefined,
                sort_index: values.sortIndex ?? 0,
                discount_amount: values.discountAmount ?? -1,
                discount_percentage: values.discountPercentage ?? 0,
                available: values.available,
                is_ticket: values.isTicket,
                is_secret: values.isSecret,
                secret_key: values.secretKey || undefined,
                imagefile_original: getFile(values.imageFile),
            },
            bodySerializer: (body) => {
                const formData = new FormData();
                formData.append("name", body.name);
                formData.append("description", body.description || "");
                formData.append("price", body.price);
                formData.append("max", String(body.max));
                if (body.max_per_order !== undefined)
                    formData.append("max_per_order", String(body.max_per_order));
                formData.append("sort_index", String(body.sort_index ?? 0));
                formData.append("discount_amount", String(body.discount_amount ?? -1));
                formData.append("discount_percentage", String(body.discount_percentage ?? 0));
                formData.append("available", body.available ? "true" : "false");
                formData.append("is_ticket", body.is_ticket ? "true" : "false");
                formData.append("is_secret", body.is_secret ? "true" : "false");
                if (body.secret_key) formData.append("secret_key", body.secret_key);
                if (body.imagefile_original)
                    formData.append("imagefile_original", body.imagefile_original);
                return formData;
            },
        });
        toast.success(t("StoreItemEditView.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("StoreItemEditView.editFailure"), {
            name: "name",
            description: "description",
            price: "price",
            max: "max",
            max_per_order: "maxPerOrder",
            sort_index: "sortIndex",
            discount_amount: "discountAmount",
            discount_percentage: "discountPercentage",
            available: "available",
            is_ticket: "isTicket",
            is_secret: "isSecret",
            secret_key: "secretKey",
            imagefile_original: "imageFile",
        });
    }
    return false;
}

async function addVariant() {
    if (!newVariantName.value.trim() || !isEditMode.value) return;

    variantSaving.value = true;
    try {
        const response = await api.adminEventStoreItemVariantsCreate({
            path: { event_pk: eventId.value },
            body: {
                item: parseInt(props.id!, 10),
                name: newVariantName.value.trim(),
            },
        });
        variants.value.push(response.data!);
        newVariantName.value = "";
    } catch (e) {
        toast.error(t("StoreItemEditView.variants.createFailure"));
        console.error(e);
    } finally {
        variantSaving.value = false;
    }
}

async function deleteVariant(variant: StoreItemVariant) {
    const text = t("StoreItemEditView.variants.deleteConfirm", variant);
    await confirmDialog.value!.ifConfirmed(text, async () => {
        try {
            await api.adminEventStoreItemVariantsDestroy({
                path: { event_pk: eventId.value, id: variant.id },
            });
            variants.value = variants.value.filter((v) => v.id !== variant.id);
            toast.success(t("StoreItemEditView.variants.deleteSuccess"));
        } catch (e) {
            toast.error(getApiErrorMessage(e, t("StoreItemEditView.variants.deleteFailure")));
            console.error(e);
        }
    });
}

function goBack() {
    router.push({ name: "store-items", params: { eventId: props.eventId } });
}

onMounted(async () => {
    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminEventStoreItemsRetrieve({
                path: { event_pk: eventId.value, id: parseInt(props.id!, 10) },
            });
            const item = response.data!;
            itemName.value = item.name;
            currentImageUrl.value = item.imagefile_thumbnail_url ?? null;
            variants.value = item.variants ?? [];
            setValues({
                name: item.name,
                description: item.description ?? "",
                price: item.price,
                max: item.max,
                maxPerOrder: item.max_per_order ?? null,
                sortIndex: item.sort_index ?? 0,
                discountAmount: item.discount_amount ?? -1,
                discountPercentage: item.discount_percentage ?? 0,
                available: item.available ?? true,
                isTicket: item.is_ticket ?? false,
                isSecret: item.is_secret ?? false,
                secretKey: item.secret_key ?? "",
            });
        } catch (e) {
            toast.error(t("StoreItemEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
