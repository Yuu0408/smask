<script setup lang="ts">
import { onBeforeMount } from 'vue';
import { RouterView, useRouter } from 'vue-router';

const router = useRouter();
onBeforeMount(() => {
    if (router.currentRoute.value.name === 'chat') {
        void router.push({
            name: 'chat.medical-record',
        });
    }
});
</script>

<template>
    <RouterView />
</template>
