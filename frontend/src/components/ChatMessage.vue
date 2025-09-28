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
                <p class="whitespace-pre-wrap leading-relaxed">{{ content }}</p>
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
import { User } from 'lucide-vue-next';
interface Props {
    role: 'human' | 'ai';
    content: string;
}
defineProps<Props>();
</script>
