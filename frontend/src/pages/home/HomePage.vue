<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { MessageCirclePlus, BookText, ListTodo } from 'lucide-vue-next';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
const { t } = useI18n();
const router = useRouter();
const { openDialog } = useDialog();
</script>

<template>
    <div class="flex-1 flex flex-col overflow-auto">
        <!-- Hero -->
        <section
            class="flex flex-col items-center justify-center text-center py-16 px-4 bg-gradient-to-b from-gray-50 to-white"
        >
            <h1 class="text-4xl font-bold tracking-tight sm:text-5xl">
                {{ t('page.home.title') }}
            </h1>
            <p class="mt-4 text-lg text-muted-foreground max-w-xl">
                {{ t('page.home.title.description') }}
            </p>
        </section>

        <!-- Quick Buttons -->
        <section
            class="py-12 px-4 sm:px-6 grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 max-w-5xl mx-auto w-full"
        >
            <Card class="flex flex-col items-center p-6">
                <CardHeader class="w-full flex justify-center p-0">
                    <MessageCirclePlus class="w-8 h-8 text-primary" />
                </CardHeader>
                <CardContent class="flex flex-col items-center">
                    <CardTitle class="mb-4">{{
                        t('page.home.card.title.start')
                    }}</CardTitle>
                    <Button
                        variant="default"
                        class="w-full sm:w-auto"
                        @click="openDialog({ component: MedicalRecordDialog })"
                    >
                        {{ t('page.home.card.button.start') }}
                    </Button>
                </CardContent>
            </Card>

            <Card class="flex flex-col items-center p-6">
                <CardHeader class="w-full flex justify-center p-0">
                    <BookText class="w-8 h-8 text-primary" />
                </CardHeader>
                <CardContent class="flex flex-col items-center">
                    <CardTitle class="mb-4">{{
                        t('page.home.card.title.record')
                    }}</CardTitle>
                    <Button
                        variant="default"
                        class="w-full sm:w-auto"
                        @click="router.push({ name: 'record' })"
                        >{{ t('page.home.card.button.open') }}</Button
                    >
                </CardContent>
            </Card>

            <Card class="flex flex-col items-center p-6">
                <CardHeader class="w-full flex justify-center p-0">
                    <ListTodo class="w-8 h-8 text-primary" />
                </CardHeader>
                <CardContent class="flex flex-col items-center">
                    <CardTitle class="mb-4">{{
                        t('page.home.card.title.todo')
                    }}</CardTitle>
                    <Button
                        variant="default"
                        class="w-full sm:w-auto"
                        @click="router.push({ name: 'todo' })"
                        >{{ t('page.home.card.button.open') }}</Button
                    >
                </CardContent>
            </Card>
        </section>

        <!-- Description / Why Section -->
        <section class="py-16 px-6 bg-gray-50">
            <div class="max-w-3xl mx-auto text-center space-y-4">
                <h2 class="text-2xl font-semibold">
                    {{ t('page.home.why.title') }}
                </h2>
                <p class="text-muted-foreground">
                    {{ t('page.home.why.description') }}
                </p>
            </div>
        </section>

        <!-- Footer removed by request -->
    </div>
</template>
