<template>
    <LayoutBase :breadcrumbs="breadcrumbs">
        <v-col v-if="loading" class="d-flex justify-center my-8">
            <v-progress-circular indeterminate size="64" />
        </v-col>
        <v-col v-else>
            <v-card>
                <v-card-text>
                    <v-form @submit.prevent="submit">
                        <v-row>
                            <v-col cols="12" md="6">
                                <v-text-field
                                    v-model="name.value.value"
                                    :error-messages="name.errorMessage.value"
                                    variant="outlined"
                                    :label="t('EntryEditView.labels.name') + ' *'"
                                />
                            </v-col>
                            <v-col cols="12" md="6">
                                <v-text-field
                                    v-model="creator.value.value"
                                    :error-messages="creator.errorMessage.value"
                                    variant="outlined"
                                    :label="t('EntryEditView.labels.creator') + ' *'"
                                />
                            </v-col>
                        </v-row>

                        <v-textarea
                            v-model="description.value.value"
                            :error-messages="description.errorMessage.value"
                            variant="outlined"
                            :label="t('EntryEditView.labels.description')"
                            rows="3"
                        />

                        <v-row>
                            <v-col cols="12" md="4">
                                <v-select
                                    v-model.number="compo.value.value"
                                    :items="compoOptions"
                                    :error-messages="compo.errorMessage.value"
                                    variant="outlined"
                                    :label="t('EntryEditView.labels.compo') + ' *'"
                                    :disabled="isEditMode"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model="platform.value.value"
                                    :error-messages="platform.errorMessage.value"
                                    variant="outlined"
                                    :label="t('EntryEditView.labels.platform')"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-autocomplete
                                    v-model.number="user.value.value"
                                    :items="userOptions"
                                    :error-messages="user.errorMessage.value"
                                    variant="outlined"
                                    :label="t('EntryEditView.labels.user') + ' *'"
                                    :disabled="isEditMode"
                                />
                            </v-col>
                        </v-row>

                        <FormSection>
                            {{ t("EntryEditView.sections.files") }}
                        </FormSection>
                        <v-row>
                            <v-col cols="12" md="4">
                                <v-file-input
                                    v-model="entryFile.value.value"
                                    variant="outlined"
                                    :label="entryFileLabel"
                                    :error-messages="entryFile.errorMessage.value"
                                    :hint="existingFiles?.entryfile_url ?? undefined"
                                    :persistent-hint="!!existingFiles?.entryfile_url"
                                    :accept="entryAccept"
                                    prepend-icon=""
                                    prepend-inner-icon="fas fa-file"
                                    :append-inner-icon="
                                        existingFiles?.entryfile_url
                                            ? 'fas fa-external-link'
                                            : undefined
                                    "
                                    @click:append-inner="openUrl(existingFiles?.entryfile_url)"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-file-input
                                    v-model="sourceFile.value.value"
                                    variant="outlined"
                                    :label="t('EntryEditView.labels.sourcefile')"
                                    :hint="existingFiles?.sourcefile_url ?? undefined"
                                    :persistent-hint="!!existingFiles?.sourcefile_url"
                                    :accept="sourceAccept"
                                    prepend-icon=""
                                    prepend-inner-icon="fas fa-code"
                                    :append-inner-icon="
                                        existingFiles?.sourcefile_url
                                            ? 'fas fa-external-link'
                                            : undefined
                                    "
                                    @click:append-inner="openUrl(existingFiles?.sourcefile_url)"
                                />
                            </v-col>
                            <v-col v-if="allowsImageFile" cols="12" md="4">
                                <v-file-input
                                    v-model="imageFile.value.value"
                                    variant="outlined"
                                    :label="imageFileLabel"
                                    :error-messages="imageFile.errorMessage.value"
                                    :hint="existingFiles?.imagefile_original_url ?? undefined"
                                    :persistent-hint="!!existingFiles?.imagefile_original_url"
                                    :accept="imageAccept"
                                    prepend-icon=""
                                    prepend-inner-icon="fas fa-image"
                                    :append-inner-icon="
                                        existingFiles?.imagefile_original_url
                                            ? 'fas fa-external-link'
                                            : undefined
                                    "
                                    @click:append-inner="
                                        openUrl(existingFiles?.imagefile_original_url)
                                    "
                                />
                            </v-col>
                        </v-row>

                        <FormSection>
                            {{ t("EntryEditView.sections.media") }}
                        </FormSection>
                        <v-row>
                            <v-col cols="12" md="8">
                                <v-text-field
                                    v-model="youtubeVideoId.value.value"
                                    :error-messages="youtubeVideoId.errorMessage.value"
                                    variant="outlined"
                                    :label="t('EntryEditView.labels.youtubeVideoId')"
                                    placeholder="e.g. dQw4w9WgXcQ"
                                />
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-text-field
                                    v-model.number="youtubeStart.value.value"
                                    type="number"
                                    :error-messages="youtubeStart.errorMessage.value"
                                    variant="outlined"
                                    :label="t('EntryEditView.labels.youtubeStart')"
                                    :min="0"
                                />
                            </v-col>
                        </v-row>

                        <FormSection v-if="isEditMode">
                            {{ t("EntryEditView.sections.ranking") }}
                        </FormSection>
                        <v-row v-if="isEditMode">
                            <v-col cols="6" md="3">
                                <div class="text-body-2 text-medium-emphasis">
                                    {{ t("EntryEditView.labels.score") }}
                                </div>
                                <div class="text-h6">{{ votingScore }}</div>
                            </v-col>
                            <v-col cols="6" md="3">
                                <div class="text-body-2 text-medium-emphasis">
                                    {{ t("EntryEditView.labels.rank") }}
                                </div>
                                <div class="text-h6">{{ votingRank }}</div>
                            </v-col>
                        </v-row>

                        <FormSection>
                            {{ t("EntryEditView.sections.disqualification") }}
                        </FormSection>
                        <DisqualificationField
                            v-model="disqualified.value.value"
                            v-model:reason="disqualifiedReason.value.value"
                            :error-message="disqualified.errorMessage.value"
                            :reason-error-message="disqualifiedReason.errorMessage.value"
                            :label-on="t('EntryEditView.labels.disqualifiedOn')"
                            :label-off="t('EntryEditView.labels.disqualifiedOff')"
                            :reason-label="t('EntryEditView.labels.disqualifiedReason')"
                        />

                        <template v-if="isEditMode && alternateFiles.length > 0">
                            <FormSection>
                                {{ t("EntryEditView.sections.alternateFiles") }}
                            </FormSection>
                            <v-list density="compact">
                                <v-list-item
                                    v-for="file in alternateFiles"
                                    :key="file.url"
                                    :href="file.url"
                                    target="_blank"
                                    :title="file.format"
                                    :subtitle="file.url"
                                >
                                    <template #prepend>
                                        <FontAwesomeIcon :icon="faDownload" class="mr-4" />
                                    </template>
                                </v-list-item>
                            </v-list>
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
import { faDownload, faFloppyDisk as faSave } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { parseInt } from "lodash-es";
import { type GenericObject, useField, useForm } from "vee-validate";
import { computed, onMounted, ref, type Ref } from "vue";
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
import type { AlternateEntryFile, Compo, CompoEntry, User } from "@/api";
import DisqualificationField from "@/components/DisqualificationField.vue";
import FormSection from "@/components/FormSection.vue";
import LayoutBase, { type BreadcrumbItem } from "@/components/LayoutBase.vue";
import { useEvents } from "@/services/events";
import { handleApiError } from "@/utils/http";

const props = defineProps<{
    eventId: string;
    id?: string;
}>();

const { t } = useI18n();
const router = useRouter();
const toast = useToast();
const { getEventById } = useEvents();

const loading = ref(false);
const saving = ref(false);
const entryName = ref<string>("");
const eventId = computed(() => parseInt(props.eventId, 10));
const isEditMode = computed(() => props.id !== undefined);

const compos: Ref<Compo[]> = ref([]);
const users: Ref<User[]> = ref([]);
const existingFiles: Ref<Pick<
    CompoEntry,
    "entryfile_url" | "sourcefile_url" | "imagefile_original_url"
> | null> = ref(null);

// Readonly data for edit mode
const votingScore = ref<string>("-");
const votingRank = ref<string>("-");
const alternateFiles: Ref<AlternateEntryFile[]> = ref([]);

// Helper to get file from v-file-input value (can be File, File[], or null)
function getFile(value: File | File[] | null | undefined): File | undefined {
    if (!value) return undefined;
    if (Array.isArray(value)) return value[0];
    return value;
}

// File type for validation
type FileValue = File | File[] | null;

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = [
        {
            title: getEventById(eventId.value)?.name ?? "...",
            to: { name: "dashboard", params: { eventId: props.eventId } },
        },
        {
            title: t("EntriesView.title"),
            to: { name: "entries", params: { eventId: props.eventId } },
        },
    ];
    if (isEditMode.value) {
        items.push({ title: entryName.value || "...", disabled: true });
    } else {
        items.push({ title: t("Breadcrumbs.newEntry"), disabled: true });
    }
    return items;
});

const compoOptions = computed(() => compos.value.map((c) => ({ title: c.name, value: c.id })));
const userOptions = computed(() => users.value.map((u) => ({ title: u.username, value: u.id })));

// Helper to get compo by ID for validation
function getCompoById(compoId: number | null): Compo | null {
    if (!compoId) return null;
    return compos.value.find((c) => c.id === compoId) ?? null;
}

const validationSchema = yupObject({
    name: yupString().required().min(1).max(64),
    creator: yupString().required().min(1).max(64),
    description: yupString(),
    compo: yupNumber().nullable().required(),
    user: yupNumber().nullable().required(),
    platform: yupString().nullable(),
    youtubeVideoId: yupString().nullable().max(32),
    youtubeStart: yupNumber().nullable().min(0),
    disqualified: yupBoolean(),
    disqualifiedReason: yupString(),
    entryFile: yupMixed()
        .nullable()
        .test("entry-file-required", t("EntryEditView.entryFileRequired"), (value) => {
            // Entry file is always required; in edit mode, existing file is also OK
            if (existingFiles.value?.entryfile_url) return true;
            return !!getFile(value as FileValue);
        }),
    sourceFile: yupMixed().nullable(),
    imageFile: yupMixed()
        .nullable()
        .test("image-file-required", t("EntryEditView.imageFileRequired"), function (value) {
            // Image file is required when compo's thumbnail_pref === 0
            const compoId = this.parent.compo;
            const selectedCompo = getCompoById(compoId);
            const requiresImage = selectedCompo?.thumbnail_pref === 0;
            if (!requiresImage) return true;
            // In edit mode, existing file is also OK
            if (existingFiles.value?.imagefile_original_url) return true;
            return !!getFile(value as FileValue);
        }),
});

const { handleSubmit, setValues, setErrors, meta } = useForm({
    validationSchema,
    initialValues: {
        name: "",
        creator: "",
        description: "",
        compo: null as number | null,
        user: null as number | null,
        platform: "",
        youtubeVideoId: "",
        youtubeStart: null as number | null,
        disqualified: false,
        disqualifiedReason: "",
        entryFile: null as FileValue,
        sourceFile: null as FileValue,
        imageFile: null as FileValue,
    },
});

const name = useField<string>("name");
const creator = useField<string>("creator");
const description = useField<string>("description");
const compo = useField<number | null>("compo");
const user = useField<number | null>("user");
const platform = useField<string>("platform");
const youtubeVideoId = useField<string>("youtubeVideoId");
const youtubeStart = useField<number | null>("youtubeStart");
const disqualified = useField<boolean>("disqualified");
const disqualifiedReason = useField<string>("disqualifiedReason");
const entryFile = useField<FileValue>("entryFile");
const sourceFile = useField<FileValue>("sourceFile");
const imageFile = useField<FileValue>("imageFile");

// Get selected compo details for format restrictions
const selectedCompo = computed(() => {
    const compoId = compo.value.value;
    if (!compoId) return null;
    return compos.value.find((c) => c.id === compoId) ?? null;
});

// Convert pipe-separated formats to accept attribute (e.g., "zip|7z" -> ".zip,.7z")
function formatsToAccept(formats: string | undefined): string | undefined {
    if (!formats) return undefined;
    return formats
        .split("|")
        .filter(Boolean)
        .map((ext) => `.${ext}`)
        .join(",");
}

// File accept attributes based on selected compo
const entryAccept = computed(() => formatsToAccept(selectedCompo.value?.formats));
const sourceAccept = computed(() => formatsToAccept(selectedCompo.value?.source_formats));
const imageAccept = computed(() => formatsToAccept(selectedCompo.value?.image_formats));

// Image file is allowed based on thumbnail_pref:
// 0 = required, 1 = use entry file (no separate image), 2 = optional, 3 = not allowed
const allowsImageFile = computed(() => {
    const pref = selectedCompo.value?.thumbnail_pref;
    return pref === 0 || pref === 2;
});

// Image file is required when thumbnail_pref is 0
const requiresImageFile = computed(() => selectedCompo.value?.thumbnail_pref === 0);

// Entry file label (always required)
const entryFileLabel = computed(() => `${t("EntryEditView.labels.entryfile")} *`);

// Dynamic label for image file field
const imageFileLabel = computed(() => {
    const base = t("EntryEditView.labels.imagefile");
    if (requiresImageFile.value) {
        return `${base} *`;
    }
    return base;
});

function openUrl(url: string | null | undefined) {
    if (url) {
        window.open(url, "_blank");
    }
}

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

// Build youtube_url object from form values
function buildYoutubeUrl(
    videoId: string | null | undefined,
    start: number | null | undefined
): { video_id: string; start?: number | null } | null {
    if (!videoId) return null;
    return {
        video_id: videoId,
        start: start ?? null,
    };
}

async function createItem(values: GenericObject) {
    try {
        await api.adminEventKompomaattiEntriesCreate({
            path: { event_pk: eventId.value },
            body: {
                name: values.name,
                creator: values.creator,
                description: values.description || "",
                compo: values.compo,
                user: values.user,
                platform: values.platform || null,
                entryfile: getFile(values.entryFile)!,
                sourcefile: getFile(values.sourceFile),
                imagefile_original: allowsImageFile.value ? getFile(values.imageFile) : undefined,
                youtube_url: buildYoutubeUrl(values.youtubeVideoId, values.youtubeStart),
                disqualified: values.disqualified,
                disqualified_reason: values.disqualifiedReason || "",
            },
            bodySerializer: (body) => {
                const formData = new FormData();
                formData.append("name", body.name);
                formData.append("creator", body.creator);
                formData.append("description", body.description);
                formData.append("compo", String(body.compo));
                formData.append("user", String(body.user));
                if (body.platform) formData.append("platform", body.platform);
                formData.append("entryfile", body.entryfile);
                if (body.sourcefile) formData.append("sourcefile", body.sourcefile);
                if (body.imagefile_original)
                    formData.append("imagefile_original", body.imagefile_original);
                if (body.youtube_url)
                    formData.append("youtube_url", JSON.stringify(body.youtube_url));
                if (body.disqualified) formData.append("disqualified", "true");
                if (body.disqualified_reason)
                    formData.append("disqualified_reason", body.disqualified_reason);
                return formData;
            },
        });
        toast.success(t("EntryEditView.createSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("EntryEditView.createFailure"));
    }
    return false;
}

async function editItem(itemId: number, values: GenericObject) {
    const hasImageFile = allowsImageFile.value && !!getFile(values.imageFile);
    const hasFiles = !!getFile(values.entryFile) || !!getFile(values.sourceFile) || hasImageFile;
    const youtubeUrl = buildYoutubeUrl(values.youtubeVideoId, values.youtubeStart);

    try {
        if (hasFiles) {
            // Use FormData when uploading files
            await api.adminEventKompomaattiEntriesPartialUpdate({
                path: { event_pk: eventId.value, id: itemId },
                body: {
                    name: values.name,
                    creator: values.creator,
                    description: values.description || "",
                    platform: values.platform || null,
                    youtube_url: youtubeUrl,
                    disqualified: values.disqualified,
                    disqualified_reason: values.disqualifiedReason || "",
                    entryfile: getFile(values.entryFile),
                    sourcefile: getFile(values.sourceFile),
                    imagefile_original: hasImageFile ? getFile(values.imageFile) : undefined,
                },
                bodySerializer: (body) => {
                    const formData = new FormData();
                    formData.append("name", body.name);
                    formData.append("creator", body.creator);
                    formData.append("description", body.description || "");
                    if (body.platform) formData.append("platform", body.platform);
                    if (body.youtube_url)
                        formData.append("youtube_url", JSON.stringify(body.youtube_url));
                    if (body.disqualified) formData.append("disqualified", "true");
                    if (body.disqualified_reason)
                        formData.append("disqualified_reason", body.disqualified_reason);
                    if (body.entryfile) formData.append("entryfile", body.entryfile);
                    if (body.sourcefile) formData.append("sourcefile", body.sourcefile);
                    if (body.imagefile_original)
                        formData.append("imagefile_original", body.imagefile_original);
                    return formData;
                },
            });
        } else {
            // Use regular JSON when no files
            await api.adminEventKompomaattiEntriesPartialUpdate({
                path: { event_pk: eventId.value, id: itemId },
                body: {
                    name: values.name,
                    creator: values.creator,
                    description: values.description || "",
                    platform: values.platform || null,
                    youtube_url: youtubeUrl,
                    disqualified: values.disqualified,
                    disqualified_reason: values.disqualifiedReason || "",
                },
            });
        }
        toast.success(t("EntryEditView.editSuccess"));
        return true;
    } catch (e) {
        handleApiError(e, setErrors, toast, t("EntryEditView.editFailure"));
    }
    return false;
}

function goBack() {
    router.push({ name: "entries", params: { eventId: props.eventId } });
}

async function loadCompos() {
    try {
        const response = await api.adminEventKompomaattiComposList({
            path: { event_pk: eventId.value },
            query: { limit: 100 },
        });
        compos.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load compos:", e);
    }
}

async function loadUsers() {
    try {
        const response = await api.adminUsersList({
            query: { limit: 1000 },
        });
        users.value = response.data!.results;
    } catch (e) {
        console.error("Failed to load users:", e);
    }
}

onMounted(async () => {
    await Promise.all([loadCompos(), loadUsers()]);

    if (isEditMode.value) {
        loading.value = true;
        try {
            const response = await api.adminEventKompomaattiEntriesRetrieve({
                path: { event_pk: eventId.value, id: parseInt(props.id!, 10) },
            });
            const item = response.data!;
            entryName.value = item.name;
            existingFiles.value = {
                entryfile_url: item.entryfile_url,
                sourcefile_url: item.sourcefile_url,
                imagefile_original_url: item.imagefile_original_url,
            };

            // Set readonly voting results
            votingScore.value = item.score?.toString() ?? "-";
            votingRank.value = item.rank?.toString() ?? "-";
            alternateFiles.value = item.alternate_files ?? [];

            setValues({
                name: item.name,
                creator: item.creator,
                description: item.description ?? "",
                compo: item.compo,
                user: item.user,
                platform: item.platform ?? "",
                youtubeVideoId: item.youtube_url?.video_id ?? "",
                youtubeStart: item.youtube_url?.start ?? null,
                disqualified: item.disqualified ?? false,
                disqualifiedReason: item.disqualified_reason ?? "",
            });
        } catch (e) {
            toast.error(t("EntryEditView.loadFailure"));
            console.error(e);
            goBack();
        } finally {
            loading.value = false;
        }
    }
});
</script>
