<template>
    <div v-if="choices?.length" class="w-full max-w-4xl px-4 pb-6">
        <div class="rounded-2xl bg-white/80 p-3 shadow-sm backdrop-blur">
            <div class="flex items-center justify-between pb-2">
                <p
                    class="text-xs uppercase tracking-[0.2em] text-muted-foreground"
                >
                    Suggested replies
                </p>
                <span class="text-[11px] text-primary font-semibold">
                    Tap to auto-fill
                </span>
            </div>
            <div class="flex flex-wrap gap-2">
                <button
                    v-for="(choice, index) in choices"
                    :key="index"
                    @click="handleChoice(choice)"
                    class="group relative overflow-hidden rounded-xl border border-primary/20 bg-gradient-to-r from-primary/5 via-white to-accent/5 px-4 py-2 text-sm font-medium text-foreground shadow-sm transition hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-md"
                >
                    <span
                        class="absolute inset-0 bg-gradient-to-r from-primary/10 via-accent/10 to-transparent opacity-0 transition group-hover:opacity-70"
                        aria-hidden="true"
                    ></span>
                    <span class="relative">{{ choice }}</span>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

defineProps<{
    choices: string[];
}>();

const emit = defineEmits<{
    (e: 'select', choice: string): void;
}>();

function handleChoice(choice: string) {
    emit('select', choice);
}
</script>
