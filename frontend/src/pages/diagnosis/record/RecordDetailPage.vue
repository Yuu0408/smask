<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import {
    Stethoscope,
    ClipboardCheck,
    AlertTriangle,
    TestTubes,
} from 'lucide-vue-next';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const { t } = useI18n();

const sections = computed(() => [
    {
        icon: ClipboardCheck,
        title: t('diagnosisPage.mostLikely'),
        badge: t('diagnosisPage.supporting'),
        items: [],
        emptyText: t('diagnosisPage.notAvailable'),
        tone: 'from-emerald-200/60 via-white to-primary/10',
    },
    {
        icon: AlertTriangle,
        title: t('diagnosisPage.ruleOut'),
        badge: t('diagnosisPage.differentiating'),
        items: [],
        emptyText: t('diagnosisPage.notAvailable'),
        tone: 'from-amber-200/60 via-white to-primary/10',
    },
    {
        icon: TestTubes,
        title: t('diagnosisPage.furtherTests'),
        badge: t('diagnosisPage.urgency'),
        items: [],
        emptyText: t('diagnosisPage.notAvailable'),
        tone: 'from-sky-200/60 via-white to-primary/10',
    },
]);
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
                    class="absolute -left-24 top-0 size-96 rounded-full bg-primary/15 blur-3xl"
                ></div>
                <div
                    class="absolute right-[-4rem] bottom-0 size-80 rounded-full bg-accent/20 blur-3xl"
                ></div>
            </div>

            <div class="relative h-full min-h-0 overflow-y-auto">
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
                                <Stethoscope class="size-4" />
                                {{ t('diagnosisPage.title') }}
                            </div>
                            <div class="space-y-1">
                                <h1
                                    class="text-3xl font-bold tracking-tight text-foreground"
                                >
                                    {{ t('diagnosisPage.title') }}
                                </h1>
                                <p class="text-muted-foreground">
                                    {{ t('diagnosisPage.notAvailable') }}
                                </p>
                            </div>
                        </div>
                        <div class="flex gap-2">
                            <Button variant="outline" class="rounded-xl">
                                {{ t('sidebar.history') }}
                            </Button>
                            <Button class="rounded-xl shadow-primary/20 shadow-lg">
                                {{ t('contact.detail.openChat') }}
                            </Button>
                        </div>
                    </header>

                    <Card
                        class="overflow-hidden border-0 bg-gradient-to-br from-primary/15 via-white to-accent/10 shadow-xl shadow-primary/20"
                    >
                        <CardHeader class="space-y-2">
                            <CardTitle class="text-lg text-primary">
                                {{ t('diagnosisPage.reasoning') }}
                            </CardTitle>
                            <p class="text-sm text-muted-foreground">
                                {{ t('diagnosisPage.notAvailable') }}
                            </p>
                        </CardHeader>
                    </Card>

                    <div class="grid gap-6 lg:grid-cols-3">
                        <Card
                            v-for="section in sections"
                            :key="section.title"
                            class="overflow-hidden border-0 shadow-lg shadow-primary/10"
                            :class="`bg-gradient-to-br ${section.tone}`"
                        >
                            <CardHeader class="space-y-1">
                                <div class="flex items-center gap-2">
                                    <component
                                        :is="section.icon"
                                        class="size-4 text-primary"
                                    />
                                    <CardTitle class="text-base">{{
                                        section.title
                                    }}</CardTitle>
                                </div>
                                <p class="text-xs font-medium text-muted-foreground">
                                    {{ section.badge }}
                                </p>
                            </CardHeader>
                            <CardContent>
                                <div
                                    v-if="!section.items.length"
                                    class="rounded-2xl border border-white/50 bg-white/50 px-4 py-3 text-sm text-muted-foreground backdrop-blur"
                                >
                                    {{ section.emptyText }}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
