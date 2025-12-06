<script setup lang="ts">
import { ref } from 'vue';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useI18n } from 'vue-i18n';
import { SendHorizonal } from 'lucide-vue-next';

const { t } = useI18n();
const emit = defineEmits<{ (e: 'send', value: string): void }>();
const props = defineProps<{ loading?: boolean }>();
const text = ref('');

function onSubmit() {
    const value = text.value.trim();
    if (!value || props.loading) return;
    emit('send', value);
    text.value = '';
}
</script>

<template>
    <form
        @submit.prevent="onSubmit"
        class="group relative overflow-hidden rounded-2xl border border-border/70 bg-white/90 px-3 py-3 backdrop-blur"
    >
        <div
            class="pointer-events-none absolute inset-0 opacity-50"
            aria-hidden="true"
        >
            <div
                class="absolute -right-6 -top-8 size-40 rounded-full bg-primary/10 blur-3xl"
            />
            <div
                class="absolute -left-12 bottom-0 size-32 rounded-full bg-accent/15 blur-3xl"
            />
        </div>

        <div class="relative flex items-end gap-3">
            <Textarea
                v-model="text"
                :placeholder="t('chatInput.placeholder')"
                class="min-h-[62px] max-h-44 w-full resize-y rounded-xl border border-border/80 bg-white/70 px-3 py-3 text-sm focus-visible:ring-2 focus-visible:ring-primary/40 dark:bg-white/5"
                :disabled="loading"
                @keydown.enter.exact.prevent="onSubmit"
            />
            <Button
                type="submit"
                :disabled="loading"
                class="mb-1 h-12 rounded-xl px-4 bg-primary text-primary-foreground transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:bg-muted disabled:text-muted-foreground"
            >
                <SendHorizonal class="mr-2 size-4" />
                <span class="font-semibold">{{
                    loading
                        ? t('common.loading')
                        : t('chat.input.send-button.send')
                }}</span>
            </Button>
        </div>
    </form>
</template>
