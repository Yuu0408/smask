<script setup lang="ts">
import { ref } from 'vue';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useI18n } from 'vue-i18n';

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
        class="flex items-end gap-2 justify-center"
    >
        <Textarea
            v-model="text"
            :placeholder="t('chatInput.placeholder')"
            class="min-h-[44px] max-h-40 w-full resize-y rounded-xl bg-muted/40 px-4 py-3 text-sm focus-visible:ring-0"
            :disabled="loading"
            @keydown.enter.exact.prevent="onSubmit"
        />
        <Button
            type="submit"
            :disabled="loading || !text.trim()"
            class="rounded-xl mb-1"
        >
            <span v-if="!loading">{{ t('chat.input.send-button.send') }}</span>
            <span v-else class="opacity-70">{{
                t('chat.input.send-button.send')
            }}</span>
        </Button>
    </form>
</template>
