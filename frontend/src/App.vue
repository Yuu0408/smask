<script setup lang="ts">
// import { useRouter } from 'vue-router';
import { RouterView } from 'vue-router';
import DialogManager from './plugins/dialog-manager/components/DialogManager.vue';
import { useDialog } from './plugins/dialog-manager/use-dialog';
import { onUnmounted } from 'vue';
import { Toaster } from './components/ui/sonner';
import 'vue-sonner/style.css';

const { closeAllDialogs } = useDialog();
// const router = useRouter();

onUnmounted(() => {
    // Close all dialogs when the app is unmounted
    closeAllDialogs();
});
</script>

<template>
    <DialogManager />
    <Toaster rich-colors />
    <RouterView />
</template>
