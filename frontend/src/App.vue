<script setup lang="ts">
import { RouterView } from 'vue-router';
import DialogManager from './plugins/dialog-manager/components/DialogManager.vue';
import { Toaster } from './components/ui/sonner';
import 'vue-sonner/style.css';
</script>

<template>
    <DialogManager />
    <Toaster rich-colors />
    <RouterView />
</template>
