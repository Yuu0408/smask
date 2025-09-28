<template>
    <div
        v-if="choices?.length"
        class="w-full max-w-2xl px-4 pb-10 flex flex-wrap gap-2 justify-center"
    >
        <button
            v-for="(choice, index) in choices"
            :key="index"
            @click="handleChoice(choice)"
            class="px-4 py-2 bg-gray-100 dark:bg-zinc-700 text-base rounded-full hover:bg-gray-200 dark:hover:bg-zinc-600 transition"
        >
            {{ choice }}
        </button>
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
