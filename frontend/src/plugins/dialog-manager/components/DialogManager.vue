<script setup lang="ts">
import { dialogUtils } from '../dialog-manager';

const { dialogStack, handleOpenChange, closeDialog } = dialogUtils;
</script>

<template>
    <template v-for="dialog in dialogStack" :key="dialog.id">
        <component
            :is="dialog.component"
            v-bind="dialog.props"
            :open="dialog.isOpen"
            @update:open="
                (isOpen: boolean) => handleOpenChange(dialog.id, isOpen)
            "
            @close="closeDialog(dialog.id)"
            @submit="(result: any) => closeDialog(dialog.id, result)"
        />
    </template>
</template>
