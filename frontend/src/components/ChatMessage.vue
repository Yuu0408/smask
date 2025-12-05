<template>
    <div class="mb-4">
        <div
            class="flex items-start gap-3"
            :class="role === 'human' ? 'justify-end' : 'justify-start'"
        >
            <!-- Assistant avatar -->
            <div v-if="role === 'ai'" class="flex-shrink-0">
                <div
                    class="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground"
                >
                    <User class="size-4" aria-hidden="true" />
                </div>
            </div>

            <!-- Bubble -->
            <div
                class="max-w-[80%] rounded-xl border bg-card px-4 py-3 text-sm shadow-sm"
                :class="
                    role === 'human'
                        ? 'bg-primary text-primary-foreground border-primary/20'
                        : 'bg-muted/50'
                "
            >
                <p
                    class="whitespace-pre-wrap leading-relaxed"
                    :class="placeholderClass"
                >
                    {{ displayText }}
                </p>
            </div>

            <!-- User avatar -->
            <div v-if="role === 'human'" class="flex-shrink-0">
                <div
                    class="flex size-8 items-center justify-center rounded-md bg-muted text-foreground"
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
    }>(),
    { pending: false }
);
const { t } = useI18n();

const displayText = computed(() => {
    const text = props.content ?? '';
    const fallback =
        t('chat.placeholder.loading') || 'AI is preparing your response...';
    if (text.trim().length > 0) return text;
    // Always show a fallback when the message text is empty to avoid a blank bubble.
    return fallback;
});

const placeholderClass = computed(() =>
    props.pending || (props.content ?? '').trim().length === 0
        ? 'italic text-muted-foreground'
        : ''
);
</script>
