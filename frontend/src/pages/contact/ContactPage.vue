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
                                    {{ t('contact.title.patients') }}
                                </div>
                                <div class="space-y-1">
                                    <h1
                                        class="text-3xl font-bold tracking-tight text-foreground"
                                    >
                                        {{ t('contact.title.patients') }}
                                    </h1>
                                    <p class="text-sm text-muted-foreground">
                                        {{
                                            t('contact.detail.startChatPrompt')
                                        }}
                                    </p>
                                </div>
                            </div>
                        </header>

                        <div
                            v-if="loading"
                            class="text-muted-foreground animate-pulse"
                        >
                            {{ t('common.loading') }}
                        </div>

                        <div
                            v-else-if="!patients.length"
                            class="text-muted-foreground"
                        >
                            <div
                                class="relative overflow-hidden rounded-3xl border border-primary/15 bg-white/80 p-10 text-center shadow-lg shadow-primary/20 backdrop-blur"
                            >
                                <div
                                    class="pointer-events-none absolute inset-0 opacity-40"
                                    aria-hidden="true"
                                >
                                    <div
                                        class="absolute -left-12 top-0 size-72 rounded-full bg-primary/10 blur-3xl"
                                    ></div>
                                    <div
                                        class="absolute right-0 bottom-0 size-64 rounded-full bg-accent/10 blur-3xl"
                                    ></div>
                                </div>
                                <div class="relative space-y-4">
                                    <p class="text-base font-medium">
                                        {{
                                            t('contact.detail.startChatPrompt')
                                        }}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div v-else class="grid gap-4 md:grid-cols-2">
                            <Card
                                v-for="p in patients"
                                :key="p.contact_id"
                                class="group cursor-pointer overflow-hidden border border-primary/10 bg-white/90 shadow-lg shadow-primary/10 transition hover:-translate-y-1 hover:shadow-xl"
                                @click="openDetail(p.contact_id)"
                            >
                                <CardHeader class="space-y-2">
                                    <CardTitle class="text-base font-semibold">
                                        {{ p.full_name }}
                                    </CardTitle>
                                    <p class="text-xs text-muted-foreground">
                                        {{ t('contact.field.age') }}:
                                        {{ p.age }}
                                    </p>
                                </CardHeader>
                                <CardContent
                                    class="text-sm text-muted-foreground"
                                >
                                    <div
                                        class="rounded-2xl bg-muted/30 px-3 py-2"
                                    >
                                        {{ p.address }}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
