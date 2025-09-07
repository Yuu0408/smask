<!-- MedicalRecordDialog.vue -->
<script setup lang="ts">
import { Dialog } from '@/components/ui/dialog';
import DialogContent from '@/components/ui/dialog/DialogContent.vue';
import DialogDescription from '@/components/ui/dialog/DialogDescription.vue';
import DialogHeader from '@/components/ui/dialog/DialogHeader.vue';
import DialogTitle from '@/components/ui/dialog/DialogTitle.vue';

import MedicalRecordForm, {
    type PatientFormValues,
} from './MedicalRecordForm.vue';

// If you exported the form values type from MedicalRecordForm, import it.
// Otherwise, you can inline a minimal shape here.
export type { PatientFormValues } from './MedicalRecordForm.vue';

const open = defineModel<boolean>(); // v-model:open from parent

const emits = defineEmits(['submit']);

const handleSubmit = (values: PatientFormValues) => {
    emits('submit', values);
};
</script>

<template>
    <Dialog v-model:open="open">
        <DialogContent class="max-h-[90vh] lg:max-w-3xl">
            <DialogHeader>
                <DialogTitle>
                    {{ $t('patientForm.dialog.title') }}
                </DialogTitle>
                <DialogDescription>
                    {{ $t('patientForm.dialog.description') }}
                </DialogDescription>
            </DialogHeader>

            <!-- Your teammate's layout expects the form to emit `submit` -->
            <MedicalRecordForm @submit="handleSubmit" />
        </DialogContent>
    </Dialog>
</template>
