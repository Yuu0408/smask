<script setup lang="ts">
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import { useI18n } from 'vue-i18n';
import { ref, type PropType } from 'vue';
import { Check, Loader2 } from 'lucide-vue-next';

const { t } = useI18n();

const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    description: {
        type: String,
        required: true,
    },
    onConfirm: {
        type: Function as PropType<() => void | Promise<void>>,
        required: true,
    },
});

const { closeLatestDialog } = useDialog();

const isConfirmed = ref(false);

const cancel = () => {
    if (isLoading.value) return;
    closeLatestDialog(false);
};
const isLoading = ref(false);

const onOpenChange = (isOpen: boolean) => {
    if (!isOpen && !isConfirmed.value) {
        cancel();
    }
};

const confirm = async () => {
    isLoading.value = true;
    try {
        await props.onConfirm();
        isConfirmed.value = true;
        closeLatestDialog(true);
    } catch {
        isLoading.value = false;
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
    <Dialog :open="true" @update:open="onOpenChange">
        <DialogContent>
            <DialogHeader>
                <DialogTitle>{{ title }}</DialogTitle>
                <DialogDescription>{{ description }}</DialogDescription>
            </DialogHeader>

            <div class="flex justify-end gap-2 pt-4">
                <Button variant="outline" @click="cancel">
                    {{ t('components.confirmation-dialog.button.cancel') }}
                </Button>
                <Button variant="destructive" @click="confirm">
                    <Loader2
                        v-if="isLoading"
                        class="animate-spin w-4 h-4 mr-2"
                    />
                    <Check v-else class="w-4 h-4 mr-2" />
                    {{ t('components.confirmation-dialog.button.confirm') }}
                </Button>
            </div>
        </DialogContent>
    </Dialog>
</template>
