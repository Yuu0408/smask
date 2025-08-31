<script setup lang="ts">
import { Label } from '@/components/ui/label';

defineProps<{
    label: string;
    value: string;
}>();
</script>

<template>
    <div
        class="flex justify-between items-start py-2 border-b last:border-none"
    >
        <Label class="font-semibold text-sm text-muted-foreground">{{
            label
        }}</Label>
        <p
            class="text-left text-sm text-gray-900 max-w-[60%] whitespace-pre-wrap break-words"
        >
            {{ value }}
        </p>
    </div>
</template>
