<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useContactStore } from '@/stores/contact';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Users2 } from 'lucide-vue-next';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

const contactStore = useContactStore();
const { user } = storeToRefs(useAuthStore());
const { t } = useI18n();
const router = useRouter();

type DoctorCard = {
    doctor_id: string;
    contact_id: string;
    username: string;
    facility?: string;
    address?: string;
};

const doctors = ref<DoctorCard[]>([]);
const loading = ref(false);
const userId = computed(() => user.value?.id ?? '');

onMounted(async () => {
    if (!userId.value) return;
    loading.value = true;
    try {
        const res = await contactStore.listMyDoctors(userId.value);
        doctors.value = (res.doctors || []).map((d) => ({ ...d }));
        // Enrich with facility/address info from contact detail
        await Promise.all(
            doctors.value.map(async (doc) => {
                try {
                    const detail = await contactStore.getContactDetail(
                        doc.contact_id
                    );
                    doc.facility = detail?.facility;
                    doc.address = detail?.address;
                } catch {
                    // ignore detail fetch errors per card
                }
            })
        );
    } finally {
        loading.value = false;
    }
});

function openChat(contactId: string) {
    router.push({ name: 'contact.chat', params: { id: contactId } });
}
</script>

<template>
    <div
        class="flex min-h-[calc(100vh-4rem)] h-[calc(100vh-4rem)] flex-col overflow-hidden"
    >
        <div class="relative flex-1 min-h-0 overflow-hidden">
            <div
                class="pointer-events-none absolute inset-0 opacity-70"
                aria-hidden="true"
            >
                <div
                    class="absolute -left-16 top-0 size-96 rounded-full bg-primary/15 blur-3xl"
                ></div>
                <div
                    class="absolute right-[-4rem] bottom-0 size-72 rounded-full bg-accent/20 blur-3xl"
                ></div>
            </div>
            <div class="relative h-full w-full flex flex-col overflow-hidden">
                <div class="flex-1 overflow-y-auto">
                    <div
                        class="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-8"
                    >
                        <header
                            class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between"
                        >
                            <div class="space-y-2">
                                <div
                                    class="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-primary"
                                >
                                    <Users2 class="size-4" />
                                    {{ t('navbar.breadcrumb.contact') }}
                                </div>
                                <div class="space-y-1">
                                    <h1
                                        class="text-3xl font-bold tracking-tight text-foreground"
                                    >
                                        {{ t('navbar.breadcrumb.contact') }}
                                    </h1>
                                    <p class="text-sm text-muted-foreground">
                                        {{ t('contact.detail.startChatPrompt') }}
                                    </p>
                                </div>
                            </div>
                        </header>

                        <div v-if="loading" class="text-muted-foreground">
                            {{ t('common.loading') }}
                        </div>
                        <div v-else-if="!doctors.length" class="text-muted-foreground">
                            {{ t('contact.detail.startChatPrompt') }}
                        </div>
                        <div v-else class="grid gap-4 md:grid-cols-2">
                            <Card
                                v-for="doc in doctors"
                                :key="doc.contact_id"
                                class="group cursor-pointer overflow-hidden border border-primary/10 bg-white/90 shadow-lg shadow-primary/10 transition hover:-translate-y-1 hover:shadow-xl"
                                @click="openChat(doc.contact_id)"
                            >
                                <CardHeader class="space-y-2">
                                    <div class="flex items-center gap-2">
                                        <span class="inline-flex items-center justify-center rounded-xl bg-primary/10 p-2 text-primary">
                                            <Users2 class="w-4 h-4" />
                                        </span>
                                        <div class="min-w-0">
                                            <CardTitle class="text-base font-semibold truncate">
                                                {{ doc.username }}
                                            </CardTitle>
                                            <p class="text-xs text-muted-foreground truncate">
                                                {{ doc.address || t('medicalRecord.notAvailableShort') }}
                                            </p>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent class="space-y-3">
                                    <div class="rounded-2xl bg-muted/30 px-3 py-2 text-sm text-muted-foreground line-clamp-2">
                                        {{ doc.facility || t('medicalRecord.notAvailableShort') }}
                                    </div>
                                    <Button
                                        variant="outline"
                                        class="rounded-xl w-full group-hover:border-primary group-hover:text-primary"
                                        @click.stop="openChat(doc.contact_id)"
                                    >
                                        {{ t('contact.detail.openChat') }}
                                    </Button>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
