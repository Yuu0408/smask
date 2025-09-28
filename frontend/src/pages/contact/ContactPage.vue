<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useContactStore } from '@/stores/contact';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

const contact = useContactStore();
const { user } = storeToRefs(useAuthStore());
const patients = ref<
    { contact_id: string; full_name: string; age: number; address: string }[]
>([]);
const loading = ref(false);
const router = useRouter();
const { t } = useI18n();

onMounted(async () => {
    if (!user.value?.id) return;
    loading.value = true;
    try {
        const res = await contact.listPatients(user.value.id);
        patients.value = res.patients;
    } finally {
        loading.value = false;
    }
});

function openDetail(id: string) {
    router.push({ name: 'contact.detail', params: { id } });
}
</script>

<template>
    <div class="p-6 space-y-6 overflow-auto">
        <h1 class="text-2xl font-semibold">
            {{ t('contact.title.patients') }}
        </h1>
        <div v-if="loading" class="text-muted-foreground">
            {{ t('common.loading') }}
        </div>
        <div v-else class="grid gap-4 md:grid-cols-2">
            <Card
                v-for="p in patients"
                :key="p.contact_id"
                class="cursor-pointer"
                @click="openDetail(p.contact_id)"
            >
                <CardHeader
                    ><CardTitle>{{ p.full_name }}</CardTitle></CardHeader
                >
                <CardContent class="text-sm text-muted-foreground">
                    <div>{{ t('contact.field.age') }}: {{ p.age }}</div>
                    <div>{{ t('contact.field.address') }}: {{ p.address }}</div>
                </CardContent>
            </Card>
        </div>
    </div>
</template>
