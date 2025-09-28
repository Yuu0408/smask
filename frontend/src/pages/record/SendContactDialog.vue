<script setup lang="ts">
import { ref, computed } from 'vue';
import { Dialog } from '@/components/ui/dialog';
import DialogContent from '@/components/ui/dialog/DialogContent.vue';
import DialogHeader from '@/components/ui/dialog/DialogHeader.vue';
import DialogTitle from '@/components/ui/dialog/DialogTitle.vue';
import DialogDescription from '@/components/ui/dialog/DialogDescription.vue';
import { Button } from '@/components/ui/button';
import {
    Select,
    SelectTrigger,
    SelectValue,
    SelectContent,
    SelectItem,
} from '@/components/ui/select';
import { useContactStore } from '@/stores/contact';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
import { toast } from 'vue-sonner';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import { useI18n } from 'vue-i18n';

const open = defineModel<boolean>();
const props = defineProps<{ recordId?: string }>();
const loading = ref(false);

const includeConversation = ref(true);
const address = ref<string>('Hà Nội');
const facility = ref<string>('');

const { user } = storeToRefs(useAuthStore());
const contactStore = useContactStore();
const { closeAllDialogs } = useDialog();
const { t } = useI18n();

const canSend = computed(
    () => !!address.value && !!facility.value && !loading.value
);

async function handleSend() {
    const selectedRecordId = props.recordId || user.value?.currentRecordId;
    if (!user.value?.id || !selectedRecordId) return;
    loading.value = true;
    try {
        await contactStore.sendContact({
            user_id: user.value.id,
            record_id: selectedRecordId,
            include_conversation: includeConversation.value,
            address: address.value,
            facility: facility.value,
        });
        toast.success(t('sendContact.toast.success'));
        open.value = false;
        closeAllDialogs();
    } catch (e: any) {
        const status = e?.response?.status;
        if (status === 409) {
            toast.error(t('sendContact.toast.alreadySent'));
        } else {
            toast.error(t('sendContact.toast.failed'));
        }
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <Dialog v-model:open="open">
        <DialogContent class="max-w-lg">
            <DialogHeader>
                <DialogTitle>{{ t('sendContact.title') }}</DialogTitle>
                <DialogDescription>{{
                    t('sendContact.description')
                }}</DialogDescription>
            </DialogHeader>

            <div class="space-y-4">
                <div class="space-y-2">
                    <div class="font-medium">
                        {{ t('sendContact.includeConversation') }}
                    </div>
                    <div class="flex gap-3">
                        <Button
                            :variant="
                                includeConversation ? 'default' : 'outline'
                            "
                            @click="includeConversation = true"
                            >{{ t('common.yes') }}</Button
                        >
                        <Button
                            :variant="
                                !includeConversation ? 'default' : 'outline'
                            "
                            @click="includeConversation = false"
                            >{{ t('common.no') }}</Button
                        >
                    </div>
                </div>

                <div class="space-y-2">
                    <div class="font-medium">
                        {{ t('sendContact.chooseAddress') }}
                    </div>
                    <Select v-model="address">
                        <SelectTrigger
                            ><SelectValue
                                :placeholder="t('sendContact.selectAddress')"
                        /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="Hà Nội">Hà Nội</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div class="space-y-2">
                    <div class="font-medium">
                        {{ t('sendContact.chooseHospital') }}
                    </div>
                    <Select v-model="facility" :disabled="!address">
                        <SelectTrigger
                            ><SelectValue
                                :placeholder="t('sendContact.selectHospital')"
                        /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="Bệnh Viện Bạch Mai"
                                >Bệnh Viện Bạch Mai</SelectItem
                            >
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <div class="pt-4 flex justify-end">
                <Button :disabled="!canSend" @click="handleSend">
                    <span v-if="loading">{{ t('sendContact.sending') }}</span>
                    <span v-else>{{ t('sendContact.send') }}</span>
                </Button>
            </div>
        </DialogContent>
    </Dialog>
</template>
