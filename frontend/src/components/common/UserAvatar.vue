<script lang="ts" setup>
import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { computed } from 'vue';

const props = defineProps<{
    name: string;
    imageLink?: string;
    class?: string;
}>();

const initials = computed(() => {
    return props.name
        .split(' ')
        .filter((word) => word.length > 0)
        .map((word) => {
            const firstAlpha = [...word].find((char) => /^[a-zA-Z]/.test(char));
            return firstAlpha || '';
        })
        .filter((char) => char !== '')
        .join('')
        .toUpperCase()
        .substring(0, 2);
});
</script>

<template>
    <Avatar :class="cn('rounded-lg size-8', props.class)">
        <AvatarImage
            v-if="props.imageLink"
            :src="props.imageLink"
            :alt="props.name"
        />
        <AvatarFallback class="rounded-lg">{{ initials }}</AvatarFallback>
    </Avatar>
</template>
