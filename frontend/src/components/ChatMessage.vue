<template>
    <div class="mb-4">
        <div
            class="flex items-start gap-3"
            :class="role === 'human' ? 'justify-end' : 'justify-start'"
        >
            <div v-if="role === 'ai'" class="flex-shrink-0 pt-1">
                <div
                    class="flex size-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary/15 to-accent/20 text-primary shadow-sm"
                >
                    <User class="size-4" aria-hidden="true" />
                </div>
            </div>

            <div class="max-w-[78%] space-y-2">
                <div
                    class="flex w-full flex-wrap items-center gap-2 text-[11px] uppercase tracking-[0.18em] text-muted-foreground/80"
                    :class="role === 'human' ? 'justify-end' : 'justify-start'"
                >
                    <span
                        class="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-[11px] font-semibold text-primary"
                    >
                        {{ roleLabel }}
                    </span>
                    <span
                        v-if="pending"
                        class="flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-semibold text-amber-800"
                    >
                        <span
                            class="size-2 rounded-full bg-amber-500 animate-pulse"
                        ></span>
                        {{ t('chat.placeholder.loading') }}
                    </span>
                </div>
                <div
                    class="relative overflow-hidden rounded-2xl border px-4 py-3 text-sm leading-relaxed shadow-sm"
                    :class="
                        role === 'human'
                            ? 'border-primary/25 bg-gradient-to-br from-primary to-primary/90 text-primary-foreground shadow-primary/30 shadow-lg'
                            : 'border-primary/10 bg-white/90 text-foreground shadow-sm dark:bg-white/5'
                    "
                >
                    <div
                        v-if="role === 'ai'"
                        class="pointer-events-none absolute inset-y-0 right-0 w-20 bg-gradient-to-l from-primary/5 to-transparent"
                        aria-hidden="true"
                    />
                    <p class="whitespace-pre-wrap" :class="placeholderClass">
                        {{ displayText }}
                    </p>
                </div>
            </div>

            <div v-if="role === 'human'" class="flex-shrink-0 pt-1">
                <div
                    class="flex size-9 items-center justify-center rounded-xl bg-muted text-foreground shadow-sm"
                >
                    <User class="size-4" aria-hidden="true" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { User } from 'lucide-vue-next';
const props = withDefaults(
    defineProps<{
        role: 'human' | 'ai';
        content: string;
        pending?: boolean;
        humanLabel?: string;
        aiLabel?: string;
    }>(),
    { pending: false }
);
const { t } = useI18n();

const displayText = computed(() => {
    const text = props.content ?? '';
    const waitingText = t('chat.placeholder.waiting');
    const loadingText = t('chat.placeholder.loading');
    const fallback =
        (waitingText &&
            waitingText !== 'chat.placeholder.waiting' &&
            waitingText) ||
        (loadingText &&
            loadingText !== 'chat.placeholder.loading' &&
            loadingText) ||
        'AI is preparing your response...';
    if (text.trim().length > 0) return text;
    // Always show a fallback when the message text is empty to avoid a blank bubble.
    return fallback;
});

const roleLabel = computed(() =>
    props.role === 'human'
        ? props.humanLabel || 'You'
        : props.aiLabel || 'Medee AI'
);

const placeholderClass = computed(() =>
    props.pending || (props.content ?? '').trim().length === 0
        ? 'italic text-muted-foreground'
        : ''
);
</script>
