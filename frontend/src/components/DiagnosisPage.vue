<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore';
import { useRouter } from 'vue-router';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useI18n } from 'vue-i18n';
import type { DiagnosisPaper } from '@/types/diagnosisPaper';

const store = useUserStore();
const router = useRouter();
const diagnosis = computed<DiagnosisPaper | null>(() => store.diagnosis);
const { t } = useI18n();

onMounted(() => {
    if (!diagnosis.value) {
        router.push('/chat');
    }
});

const isDiagnosisEmpty = computed(() => {
    return !diagnosis.value || Object.keys(diagnosis.value).length === 0;
});
</script>

<template>
    <div class="max-w-3xl w-full mx-auto p-6 space-y-8 pb-24">
        <h1 class="text-3xl font-bold text-center mb-8">
            {{ t('diagnosisPage.title') }}
        </h1>

        <div v-if="isDiagnosisEmpty" class="text-center text-gray-500">
            {{ t('diagnosisPage.notAvailable') }}
        </div>

        <template v-else>
            <!-- Reasoning -->
            <Card
                v-if="diagnosis?.reasoning_process"
                class="shadow-md hover:shadow-lg transition duration-300"
            >
                <CardHeader class="bg-muted/20 rounded-t-md px-4 pt-2">
                    <CardTitle class="text-lg font-semibold"
                        >🧠 {{ t('diagnosisPage.reasoning') }}</CardTitle
                    >
                </CardHeader>
                <CardContent
                    class="text-sm leading-relaxed text-gray-700 dark:text-gray-300 px-4 pt-2 pb-4"
                >
                    {{ diagnosis.reasoning_process }}
                </CardContent>
            </Card>

            <!-- Most Likely Diagnosis -->
            <Card
                v-if="diagnosis?.diagnosis?.most_likely"
                class="shadow-md hover:shadow-lg transition duration-300"
            >
                <CardHeader class="bg-muted/20 rounded-t-md px-4 pt-2">
                    <CardTitle class="text-lg font-semibold text-green-600"
                        >✅ {{ t('diagnosisPage.mostLikely') }}</CardTitle
                    >
                </CardHeader>
                <CardContent class="px-4 pt-2 pb-4 space-y-2">
                    <h3 class="font-semibold text-xl">
                        {{ diagnosis.diagnosis.most_likely.name }}
                    </h3>
                    <p class="text-sm text-gray-500">
                        <strong
                            >{{ t('diagnosisPage.differentiating') }}:</strong
                        >
                        {{
                            diagnosis.diagnosis.most_likely
                                .differentiating_factor ||
                            t('diagnosisPage.notAvailableShort')
                        }}
                    </p>
                    <p class="font-medium">
                        {{ t('diagnosisPage.supporting') }}:
                    </p>
                    <ul
                        class="list-disc pl-6 text-sm text-gray-700 dark:text-gray-300 space-y-1"
                    >
                        <li
                            v-for="(item, idx) in diagnosis.diagnosis
                                .most_likely.supporting_evidence"
                            :key="idx"
                        >
                            {{ item }}
                        </li>
                    </ul>
                </CardContent>
            </Card>

            <!-- Possible Diagnoses -->
            <Card
                v-if="diagnosis?.diagnosis?.possible_diagnoses?.length"
                class="shadow-md hover:shadow-lg transition duration-300"
            >
                <CardHeader class="bg-muted/20 rounded-t-md px-4 pt-2">
                    <CardTitle class="text-lg font-semibold"
                        >📋 {{ t('diagnosisPage.possible') }}</CardTitle
                    >
                </CardHeader>
                <CardContent class="space-y-6 px-4 pt-2 pb-4">
                    <div
                        v-for="(diag, idx) in diagnosis.diagnosis
                            .possible_diagnoses"
                        :key="'possible-' + idx"
                        class="border-b pb-4"
                    >
                        <h3 class="font-semibold text-xl pb-2">
                            {{ diag.name }}
                        </h3>
                        <p class="text-sm text-gray-500 pb-2">
                            <strong
                                >{{
                                    t('diagnosisPage.differentiating')
                                }}:</strong
                            >
                            {{
                                diag.differentiating_factor ||
                                t('diagnosisPage.notAvailableShort')
                            }}
                        </p>
                        <p class="font-medium pb-1">
                            {{ t('diagnosisPage.supporting') }}:
                        </p>
                        <ul
                            class="list-disc pl-6 text-sm text-gray-700 dark:text-gray-300 space-y-1 mt-1 pb-1"
                        >
                            <li
                                v-for="(item, i) in diag.supporting_evidence"
                                :key="i"
                            >
                                {{ item }}
                            </li>
                        </ul>
                    </div>
                </CardContent>
            </Card>

            <!-- Rule Out -->
            <Card
                v-if="diagnosis?.diagnosis?.rule_out?.length"
                class="shadow-md hover:shadow-lg transition duration-300"
            >
                <CardHeader class="bg-muted/20 rounded-t-md px-4 pt-2">
                    <CardTitle class="text-lg font-semibold text-red-600"
                        >❌ {{ t('diagnosisPage.ruleOut') }}</CardTitle
                    >
                </CardHeader>
                <CardContent class="space-y-6 px-4 pt-2 pb-4">
                    <div
                        v-for="(diag, idx) in diagnosis.diagnosis.rule_out"
                        :key="'ruleout-' + idx"
                        class="border-b pb-4"
                    >
                        <h3 class="font-semibold text-xl pb-2">
                            {{ diag.name }}
                        </h3>
                        <ul
                            class="list-disc pl-6 text-sm text-gray-700 dark:text-gray-300 space-y-1 mt-1"
                        >
                            <li
                                v-for="(item, i) in diag.supporting_evidence"
                                :key="i"
                            >
                                {{ item }}
                            </li>
                        </ul>
                    </div>
                </CardContent>
            </Card>

            <!-- Further Tests -->
            <Card
                v-if="diagnosis?.further_test?.length"
                class="shadow-md hover:shadow-lg transition duration-300"
            >
                <CardHeader class="bg-muted/20 rounded-t-md px-4 pt-2">
                    <CardTitle class="text-lg font-semibold"
                        >🔬 {{ t('diagnosisPage.furtherTests') }}</CardTitle
                    >
                </CardHeader>
                <CardContent class="space-y-6 px-4 pt-2 pb-4">
                    <div
                        v-for="(test, idx) in diagnosis.further_test"
                        :key="'test-' + idx"
                        class="border-b pb-4"
                    >
                        <h3 class="font-semibold text-xl pb-2">
                            {{ test.name }}
                        </h3>
                        <p
                            class="text-sm text-gray-600 dark:text-gray-400 mt-1"
                        >
                            {{ test.purpose }}
                        </p>
                        <div class="mt-3 flex flex-wrap gap-2">
                            <Badge
                                v-for="(rel, i) in test.related_condition"
                                :key="i"
                                class="rounded-md text-xs"
                                >{{ rel }}</Badge
                            >
                        </div>
                        <p class="text-sm text-red-700 mt-2">
                            <strong>{{ t('diagnosisPage.urgency') }}:</strong>
                            {{ test.urgency || t('diagnosisPage.routine') }}
                        </p>
                    </div>
                </CardContent>
            </Card>
        </template>
    </div>
</template>
