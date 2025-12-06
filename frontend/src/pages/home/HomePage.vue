<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import {
    ArrowRight,
    BookText,
    HeartPulse,
    MessageCirclePlus,
    Sparkles,
    ClipboardList,
} from 'lucide-vue-next';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { computed } from 'vue';
import ChatMessage from '@/components/ChatMessage.vue';
import ChatMultipleChoices from '@/components/ChatMultipleChoices.vue';

const { t } = useI18n();
const router = useRouter();
const { openDialog } = useDialog();

const previewMessages = computed(() => [
    { role: 'ai', text: t('page.home.preview.message1') as string },
    { role: 'human', text: t('page.home.preview.message2') as string },
    { role: 'ai', text: t('page.home.preview.message3') as string },
]);

const sampleChoices = computed(() => [
    t('page.home.preview.choice1') as string,
    t('page.home.preview.choice2') as string,
    t('page.home.preview.choice3') as string,
]);
</script>

<template>
    <div class="flex-1 flex flex-col overflow-hidden">
        <section class="relative isolate px-4 py-10 sm:py-10 overflow-hidden">
            <div
                class="pointer-events-none absolute inset-0 opacity-80"
                aria-hidden="true"
            >
                <div
                    class="absolute -left-24 top-0 size-80 rounded-full bg-primary/15 blur-3xl"
                ></div>
                <div
                    class="absolute right-0 top-12 size-96 rounded-full bg-accent/20 blur-3xl"
                ></div>
                <div
                    class="absolute -right-20 bottom-0 size-80 rounded-full bg-primary/10 blur-[120px]"
                ></div>
            </div>

            <div
                class="relative mx-auto grid max-w-5xl gap-8 lg:grid-cols-[1.05fr,0.95fr]"
            >
                <div class="space-y-6">
                    <span
                        class="inline-flex items-center gap-2 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-primary"
                    >
                        <HeartPulse class="size-4" />
                        {{ t('page.home.badge') }}
                    </span>
                    <div class="space-y-2">
                        <h1
                            class="text-4xl font-bold leading-tight tracking-tight sm:text-5xl"
                        >
                            {{ t('page.home.title') }}
                        </h1>
                        <p class="text-lg text-muted-foreground max-w-4xl">
                            {{ t('page.home.title.description') }}
                        </p>
                    </div>

                    <div class="flex flex-wrap gap-3">
                        <Button
                            size="lg"
                            class="rounded-xl shadow-md shadow-primary/15"
                            @click="
                                openDialog({ component: MedicalRecordDialog })
                            "
                        >
                            {{ t('page.home.card.button.start') }}
                            <ArrowRight class="ml-2 size-4" />
                        </Button>
                        <Button
                            size="lg"
                            variant="outline"
                            class="rounded-xl border-primary/30 text-foreground hover:bg-primary hover:text-primary-foreground"
                            @click="router.push({ name: 'record' })"
                        >
                            {{ t('page.home.card.title.record') }}
                        </Button>
                        <Button
                            size="lg"
                            variant="outline"
                            class="rounded-xl border-primary/30 text-foreground hover:bg-primary hover:text-primary-foreground"
                            @click="router.push({ name: 'todo' })"
                        >
                            {{ t('page.home.card.title.todo') }}
                        </Button>
                    </div>
                </div>

                <div class="relative">
                    <div
                        class="relative overflow-hidden rounded-3xl border border-primary/10 bg-gradient-to-br from-primary/5 via-background/50 to-accent/10 shadow-xl shadow-primary/10 backdrop-blur"
                    >
                        <div
                            class="flex items-center justify-between border-b border-border/70 px-5 py-4"
                        >
                            <div>
                                <p class="text-xs text-muted-foreground">
                                    {{ t('page.home.preview.title') }}
                                </p>
                                <p class="text-base font-semibold">
                                    {{ t('page.home.preview.subtitle') }}
                                </p>
                            </div>
                            <span
                                class="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700"
                            >
                                <Sparkles class="size-4" />
                                {{ t('chat.session.live') }}
                            </span>
                        </div>

                        <section
                            class="relative grid h-full min-h-full grid-rows-[1fr_auto] overflow-hidden rounded-none border-0 bg-white/90"
                        >
                            <div
                                class="relative min-h-0 flex-1 space-y-4 overflow-y-auto px-4 py-4"
                            >
                                <ChatMessage
                                    v-for="(message, index) in previewMessages"
                                    :key="index"
                                    :role="message.role"
                                    :content="message.text"
                                />
                            </div>

                            <div class="relative px-4 pb-4">
                                <div
                                    v-if="sampleChoices.length"
                                    class="pointer-events-none absolute inset-x-0 top-0 h-8 bg-gradient-to-b from-transparent via-white/70 to-white opacity-90"
                                    aria-hidden="true"
                                />
                                <div
                                    v-if="sampleChoices.length"
                                    class="relative z-10 grid gap-2"
                                    :class="
                                        sampleChoices.length > 2
                                            ? 'grid-cols-2'
                                            : 'grid-cols-1'
                                    "
                                >
                                    <div
                                        class="absolute -left-1 -top-6 text-primary"
                                    >
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            class="size-5"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                            stroke-width="1.8"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                        >
                                            <path
                                                d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"
                                            />
                                            <path d="M20 3v4" />
                                            <path d="M22 5h-4" />
                                            <path d="M4 17v2" />
                                            <path d="M5 18H3" />
                                        </svg>
                                    </div>
                                    <button
                                        v-for="choice in sampleChoices"
                                        :key="choice"
                                        type="button"
                                        class="w-full rounded-xl border border-primary/15 bg-gradient-to-r from-primary/5 via-white to-accent/10 px-3 py-2 text-left text-sm font-medium text-primary shadow-sm transition hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-md hover:bg-primary hover:text-primary-foreground hover:bg-none"
                                    >
                                        {{ choice }}
                                    </button>
                                </div>
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>
