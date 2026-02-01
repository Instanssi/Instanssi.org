<template>
    <div class="social-links-cell">
        <a
            v-if="homeUrl"
            :href="homeUrl"
            target="_blank"
            class="social-link"
            :title="t('SocialLinksCell.home')"
        >
            <FontAwesomeIcon :icon="faHouse" />
        </a>
        <a
            v-if="twitterUrl"
            :href="twitterUrl"
            target="_blank"
            class="social-link"
            :title="t('SocialLinksCell.twitter')"
        >
            <FontAwesomeIcon :icon="faXTwitter" />
        </a>
        <a
            v-if="githubUrl"
            :href="githubUrl"
            target="_blank"
            class="social-link"
            :title="t('SocialLinksCell.github')"
        >
            <FontAwesomeIcon :icon="faGithub" />
        </a>
        <a
            v-if="facebookUrl"
            :href="facebookUrl"
            target="_blank"
            class="social-link"
            :title="t('SocialLinksCell.facebook')"
        >
            <FontAwesomeIcon :icon="faFacebook" />
        </a>
        <a
            v-if="linkedinUrl"
            :href="linkedinUrl"
            target="_blank"
            class="social-link"
            :title="t('SocialLinksCell.linkedin')"
        >
            <FontAwesomeIcon :icon="faLinkedin" />
        </a>
        <a
            v-if="wikiUrl"
            :href="wikiUrl"
            target="_blank"
            class="social-link"
            :title="t('SocialLinksCell.wikipedia')"
        >
            <FontAwesomeIcon :icon="faWikipediaW" />
        </a>
        <span v-if="!hasAnyLink" class="no-links">-</span>
    </div>
</template>

<script setup lang="ts">
import {
    faFacebook,
    faGithub,
    faLinkedin,
    faWikipediaW,
    faXTwitter,
} from "@fortawesome/free-brands-svg-icons";
import { faHouse } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps<{
    homeUrl?: string | null;
    twitterUrl?: string | null;
    githubUrl?: string | null;
    facebookUrl?: string | null;
    linkedinUrl?: string | null;
    wikiUrl?: string | null;
}>();

const { t } = useI18n();

const hasAnyLink = computed(() => {
    return !!(
        props.homeUrl ||
        props.twitterUrl ||
        props.githubUrl ||
        props.facebookUrl ||
        props.linkedinUrl ||
        props.wikiUrl
    );
});
</script>

<style scoped>
.social-links-cell {
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.social-link {
    color: inherit;
    opacity: 0.7;
    transition: opacity 0.2s;
}

.social-link:hover {
    opacity: 1;
    color: rgb(var(--v-theme-primary));
}

.no-links {
    opacity: 0.5;
}
</style>
