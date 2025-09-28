<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import AppLayout from '@/layouts/AppLayout.vue';
import DoctorLayout from '@/layouts/DoctorLayout.vue';

const auth = useAuthStore();
const layoutComponent = computed(() =>
    auth.user?.role === 'doctor' ? DoctorLayout : AppLayout
);
</script>

<template>
    <component :is="layoutComponent" />
</template>
