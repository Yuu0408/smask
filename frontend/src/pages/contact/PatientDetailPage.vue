<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useContactStore } from '@/stores/contact';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import ChatMessage from '@/components/ChatMessage.vue';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { useI18n } from 'vue-i18n';

const route = useRoute();
const router = useRouter();
const contact = useContactStore();
const detail = ref<any>(null);
const loading = ref(false);
const view = ref<'record' | 'conversation' | 'diagnosis' | 'todo' | 'contact'>(
    'record'
);
const { t, locale } = useI18n();

onMounted(async () => {
    loading.value = true;
    try {
        const id = String(route.params.id);
        detail.value = await contact.getContactDetail(id);
    } finally {
        loading.value = false;
    }
});

function goChat() {
    router.push({ name: 'contact.chat', params: { id: route.params.id } });
}

function roleForMessage(role: string) {
    // Map both AI conversation roles and direct contact roles
    if (role === 'human' || role === 'patient') return 'human';
    if (role === 'ai' || role === 'doctor' || role === 'system') return 'ai';
    return 'ai';
}

// --- i18n helpers for medical record fields/values ---
function formatDate(dateStr?: string | null): string {
    if (!dateStr) return t('medicalRecord.notAvailableShort');
    const date = new Date(dateStr);
    const loc = locale.value === 'vi' ? 'vi-VN' : 'en-US';
    return date.toLocaleDateString(loc, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });
}

function translateGender(value?: string): string {
    if (!value) return t('medicalRecord.notAvailableShort');
    const map: Record<string, string> = {
        Male: 'male',
        Female: 'female',
        Other: 'other',
    };
    return map[value] ? t(`patientForm.options.${map[value]}`) : value;
}

function translateAlcohol(value?: string): string {
    if (!value) return t('medicalRecord.notAvailableShort');
    const map: Record<string, string> = {
        never: 'never',
        occasionally: 'occasionally',
        frequently: 'frequently',
        daily: 'daily',
    };
    return map[value] ? t(`patientForm.options.${map[value]}`) : value;
}

function translateSmoking(value?: string): string {
    if (!value) return t('medicalRecord.notAvailableShort');
    const map: Record<string, string> = {
        never: 'never',
        used_to_quit: 'usedToQuit',
        current: 'currentSmoking',
    };
    return map[value] ? t(`patientForm.options.${map[value]}`) : value;
}

function translateLivingSituation(value?: string): string {
    if (!value) return t('medicalRecord.notAvailableShort');
    const map: Record<string, string> = {
        alone: 'liveAlone',
        family: 'liveWithFamily',
        assisted: 'assistedLiving',
        other: 'otherLiving',
    };
    return map[value] ? t(`patientForm.options.${map[value]}`) : value;
}

function translateDailyIndependence(value?: string): string {
    if (!value) return t('medicalRecord.notAvailableShort');
    const map: Record<string, string> = {
        yes: 'yes',
        partially: 'partially',
        needs_assistance: 'needsAssistance',
    };
    return map[value] ? t(`patientForm.options.${map[value]}`) : value;
}

function translateTravel(value?: string): string {
    if (!value) return t('medicalRecord.notAvailableShort');
    const map: Record<string, string> = {
        no: 'no',
        '14_days': 'travel14',
        '1_month': 'travelMonth',
    };
    return map[value] ? t(`patientForm.options.${map[value]}`) : value;
}

const patientInfoItems = computed(() => {
    const d = detail.value?.medical_record?.patient_info as
        | {
              full_name?: string;
              birthday?: string;
              gender?: string;
              occupation?: string;
              nationality?: string;
              address?: string;
          }
        | undefined;
    if (!d) return [] as Array<{ label: string; value: string }>;
    return [
        {
            label: t('medicalRecord.fullName'),
            value: d.full_name || t('medicalRecord.notAvailableShort'),
        },
        { label: t('medicalRecord.birthday'), value: formatDate(d.birthday) },
        { label: t('medicalRecord.gender'), value: translateGender(d.gender) },
        {
            label: t('medicalRecord.occupation'),
            value: d.occupation || t('medicalRecord.notAvailableShort'),
        },
        {
            label: t('medicalRecord.nationality'),
            value: d.nationality || t('medicalRecord.notAvailableShort'),
        },
        {
            label: t('medicalRecord.address'),
            value: d.address || t('medicalRecord.notAvailableShort'),
        },
    ];
});

const medicalHistoryItems = computed(() => {
    const d = detail.value?.medical_record?.medical_history as
        | {
              chief_complaint?: string;
              medical_history?: string;
              past_medical_history?: string;
              current_medications?: string;
              allergies?: string;
              family_medical_history?: string;
          }
        | undefined;
    if (!d) return [] as Array<{ label: string; value: string }>;
    return [
        {
            label: t('medicalRecord.chiefComplaint'),
            value: d.chief_complaint || t('medicalRecord.notAvailableShort'),
        },
        {
            label: t('medicalRecord.symptomProgression'),
            value: d.medical_history || t('medicalRecord.notAvailableShort'),
        },
        {
            label: t('medicalRecord.pastMedicalHistory'),
            value:
                d.past_medical_history || t('medicalRecord.notAvailableShort'),
        },
        {
            label: t('medicalRecord.currentMedications'),
            value: d.current_medications || t('medicalRecord.none'),
        },
        {
            label: t('medicalRecord.allergies'),
            value: d.allergies || t('medicalRecord.none'),
        },
        {
            label: t('medicalRecord.familyHistory'),
            value:
                d.family_medical_history ||
                t('medicalRecord.notAvailableShort'),
        },
    ];
});

const socialItems = computed(() => {
    const d = detail.value?.medical_record?.social_information as
        | {
              alcohol_consumption?: string;
              alcohol_details?: any;
              smoking_habit?: string;
              smoking_details?: any;
              living_situation?: string;
              daily_activity_independence?: string;
              recent_travel_history?: string;
          }
        | undefined;
    if (!d) return [] as Array<{ label: string; value: string }>;
    const items: Array<{ label: string; value: string }> = [
        {
            label: t('medicalRecord.alcohol'),
            value: translateAlcohol(d.alcohol_consumption),
        },
        {
            label: t('medicalRecord.smoking'),
            value: translateSmoking(d.smoking_habit),
        },
        {
            label: t('medicalRecord.livingSituation'),
            value: translateLivingSituation(d.living_situation),
        },
        {
            label: t('medicalRecord.dailyActivity'),
            value: translateDailyIndependence(d.daily_activity_independence),
        },
        {
            label: t('medicalRecord.travelHistory'),
            value: translateTravel(d.recent_travel_history),
        },
    ];
    if (
        d.alcohol_consumption &&
        d.alcohol_consumption !== 'never' &&
        d.alcohol_details
    ) {
        const ad = d.alcohol_details || {};
        let desc = '';
        if (d.alcohol_consumption === 'occasionally') {
            desc = `${t('patientForm.alcoholDetails.perMonthTimes')}: ${ad.per_month_times ?? '-'}, ${t('patientForm.alcoholDetails.perTimeMl')}: ${ad.per_time_ml ?? '-'} ml, ${t('patientForm.alcoholDetails.drinkType')}: ${ad.drink_type ?? '-'}`;
        } else if (d.alcohol_consumption === 'frequently') {
            desc = `${t('patientForm.alcoholDetails.perWeekTimes')}: ${ad.per_week_times ?? '-'}, ${t('patientForm.alcoholDetails.avgPerDayMl')}: ${ad.avg_per_day_ml ?? '-'} ml, ${t('patientForm.alcoholDetails.drinkType')}: ${ad.drink_type ?? '-'}`;
        } else if (d.alcohol_consumption === 'daily') {
            desc = `${t('patientForm.alcoholDetails.avgPerDayMl')}: ${ad.avg_per_day_ml ?? '-'} ml, ${t('patientForm.alcoholDetails.drinkType')}: ${ad.drink_type ?? '-'}`;
        }
        items.splice(1, 0, { label: t('medicalRecord.alcohol'), value: desc });
    }
    if (d.smoking_habit && d.smoking_habit !== 'never' && d.smoking_details) {
        const sd = d.smoking_details || {};
        let desc = '';
        if (d.smoking_habit === 'used_to_quit') {
            const years =
                sd.years_smoked ??
                (sd.end_age != null && sd.start_age != null
                    ? sd.end_age - sd.start_age
                    : undefined);
            desc = `${t('patientForm.smokingDetails.startAge')}: ${sd.start_age ?? '-'} → ${t('patientForm.smokingDetails.endAge')}: ${sd.end_age ?? '-'}${years != null ? ` (~${years})` : ''}, ${t('patientForm.smokingDetails.cigarettesPerDay')}: ${sd.cigarettes_per_day ?? '-'}`;
        } else if (d.smoking_habit === 'current') {
            desc = `${t('patientForm.smokingDetails.startAge')}: ${sd.start_age ?? '-'} → now, ${t('patientForm.smokingDetails.cigarettesPerDay')}: ${sd.cigarettes_per_day ?? '-'}`;
        }
        items.splice(3, 0, { label: t('medicalRecord.smoking'), value: desc });
    }
    return items;
});

const obgynItems = computed(() => {
    const d = detail.value?.medical_record?.obstetric_gynecological_history as
        | {
              menstruation_status?: string;
              menstrual_cycle?: string;
              recent_sexual_activity?: boolean | null;
          }
        | undefined;
    if (!d) return [] as Array<{ label: string; value: string }>;
    return [
        {
            label: t('medicalRecord.menstruationStatus'),
            value:
                d.menstruation_status || t('medicalRecord.notAvailableShort'),
        },
        {
            label: t('medicalRecord.menstrualCycle'),
            value: d.menstrual_cycle || t('medicalRecord.notAvailableShort'),
        },
        {
            label: t('medicalRecord.sexualActivity'),
            value:
                d.recent_sexual_activity == null
                    ? t('medicalRecord.notAvailableShort')
                    : d.recent_sexual_activity
                      ? t('medicalRecord.yes')
                      : t('medicalRecord.no'),
        },
    ];
});
</script>

<template>
    <div v-if="!loading && detail" class="flex h-full min-h-0 flex-col">
        <!-- Sticky top nav -->
        <div
            class="sticky top-0 z-10 w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60"
        >
            <div
                class="mx-auto w-full max-w-4xl px-4 py-3 flex items-center justify-between gap-4"
            >
                <div class="truncate text-xl font-semibold">
                    {{
                        detail.medical_record?.patient_info?.full_name ||
                        t('contact.patient')
                    }}
                </div>
                <div class="flex flex-wrap gap-2">
                    <Button
                        :variant="view === 'record' ? 'default' : 'outline'"
                        @click="view = 'record'"
                        >{{
                            t('medicalRecord.title') ||
                            t('sidebar.medicalRecord')
                        }}</Button
                    >
                    <Button
                        :variant="
                            view === 'conversation' ? 'default' : 'outline'
                        "
                        @click="view = 'conversation'"
                        >{{ t('contact.detail.view.conversation') }}</Button
                    >
                    <Button
                        :variant="view === 'diagnosis' ? 'default' : 'outline'"
                        @click="view = 'diagnosis'"
                        >{{ t('sidebar.diagnosis') }}</Button
                    >
                    <Button
                        :variant="view === 'todo' ? 'default' : 'outline'"
                        @click="view = 'todo'"
                        >{{ t('sidebar.todoList') }}</Button
                    >
                    <Button variant="secondary" @click="goChat">{{
                        t('contact.detail.openChat')
                    }}</Button>
                </div>
            </div>
        </div>

        <!-- Scrollable content area -->
        <div class="flex-1 overflow-y-auto">
            <div class="mx-auto w-full max-w-4xl p-4 space-y-4 mb-8">
                <template v-if="view === 'record'">
                    <Card>
                        <CardHeader
                            ><CardTitle>{{
                                t('medicalRecord.patientInfo')
                            }}</CardTitle></CardHeader
                        >
                        <CardContent>
                            <dl class="divide-y divide-border">
                                <div
                                    class="py-2 grid grid-cols-3 gap-4"
                                    v-for="item in patientInfoItems"
                                    :key="'pi-' + item.label"
                                >
                                    <dt class="text-sm text-muted-foreground">
                                        {{ item.label }}
                                    </dt>
                                    <dd class="col-span-2 text-sm">
                                        {{ item.value }}
                                    </dd>
                                </div>
                            </dl>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader
                            ><CardTitle>{{
                                t('medicalRecord.medicalHistory')
                            }}</CardTitle></CardHeader
                        >
                        <CardContent>
                            <dl class="divide-y divide-border">
                                <div
                                    class="py-2 grid grid-cols-3 gap-4"
                                    v-for="item in medicalHistoryItems"
                                    :key="'mh-' + item.label"
                                >
                                    <dt class="text-sm text-muted-foreground">
                                        {{ item.label }}
                                    </dt>
                                    <dd class="col-span-2 text-sm">
                                        {{ item.value }}
                                    </dd>
                                </div>
                            </dl>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader
                            ><CardTitle>{{
                                t('medicalRecord.socialInfo')
                            }}</CardTitle></CardHeader
                        >
                        <CardContent>
                            <dl class="divide-y divide-border">
                                <div
                                    class="py-2 grid grid-cols-3 gap-4"
                                    v-for="item in socialItems"
                                    :key="'si-' + item.label"
                                >
                                    <dt class="text-sm text-muted-foreground">
                                        {{ item.label }}
                                    </dt>
                                    <dd class="col-span-2 text-sm">
                                        {{ item.value }}
                                    </dd>
                                </div>
                            </dl>
                        </CardContent>
                    </Card>

                    <Card
                        v-if="
                            detail.medical_record
                                ?.obstetric_gynecological_history
                        "
                    >
                        <CardHeader
                            ><CardTitle>{{
                                t('medicalRecord.obstetric')
                            }}</CardTitle></CardHeader
                        >
                        <CardContent>
                            <dl class="divide-y divide-border">
                                <div
                                    class="py-2 grid grid-cols-3 gap-4"
                                    v-for="item in obgynItems"
                                    :key="'ob-' + item.label"
                                >
                                    <dt class="text-sm text-muted-foreground">
                                        {{ item.label }}
                                    </dt>
                                    <dd class="col-span-2 text-sm">
                                        {{ item.value }}
                                    </dd>
                                </div>
                            </dl>
                        </CardContent>
                    </Card>
                </template>

                <template v-else-if="view === 'conversation'">
                    <h2 class="font-semibold">Conversation Snapshot</h2>
                    <div class="space-y-2">
                        <ChatMessage
                            v-for="m in detail.conversation || []"
                            :key="m.id"
                            :role="roleForMessage(m.role)"
                            :content="m.content"
                        />
                    </div>
                </template>

                <template v-else-if="view === 'diagnosis'">
                    <div class="space-y-4 mb-4">
                        <h2 class="text-2xl font-semibold">
                            {{ t('sidebar.diagnosis') }}
                        </h2>

                        <Card
                            v-if="detail.reasoning_process"
                            class="shadow-md hover:shadow-lg transition duration-300"
                        >
                            <CardHeader
                                class="bg-muted/20 rounded-t-md px-4 pt-2"
                            >
                                <CardTitle class="text-lg font-semibold"
                                    >🧠
                                    {{
                                        t('diagnosisPage.reasoning')
                                    }}</CardTitle
                                >
                            </CardHeader>
                            <CardContent
                                class="text-sm leading-relaxed text-gray-700 dark:text-gray-300 px-4 pt-2 pb-4"
                            >
                                {{ detail.reasoning_process }}
                            </CardContent>
                        </Card>

                        <Card
                            v-if="detail.diagnosis?.most_likely"
                            class="shadow-md hover:shadow-lg transition duration-300"
                        >
                            <CardHeader
                                class="bg-muted/20 rounded-t-md px-4 pt-2"
                            >
                                <CardTitle
                                    class="text-lg font-semibold text-green-600"
                                    >✅
                                    {{
                                        t('diagnosisPage.mostLikely')
                                    }}</CardTitle
                                >
                            </CardHeader>
                            <CardContent class="px-4 pt-2 pb-4 space-y-2">
                                <h3 class="font-semibold text-xl">
                                    {{ detail.diagnosis.most_likely.name }}
                                </h3>
                                <p class="text-sm text-gray-500">
                                    <strong
                                        >{{
                                            t('diagnosisPage.differentiating')
                                        }}:</strong
                                    >
                                    {{
                                        detail.diagnosis.most_likely
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
                                        v-for="(item, idx) in detail.diagnosis
                                            .most_likely.supporting_evidence"
                                        :key="'ml-' + idx"
                                    >
                                        {{ item }}
                                    </li>
                                </ul>
                            </CardContent>
                        </Card>

                        <Card
                            v-if="detail.diagnosis?.possible_diagnoses?.length"
                            class="shadow-md hover:shadow-lg transition duration-300"
                        >
                            <CardHeader
                                class="bg-muted/20 rounded-t-md px-4 pt-2"
                            >
                                <CardTitle class="text-lg font-semibold"
                                    >📋
                                    {{ t('diagnosisPage.possible') }}</CardTitle
                                >
                            </CardHeader>
                            <CardContent class="space-y-6 px-4 pt-2 pb-4">
                                <div
                                    v-for="(diag, idx) in detail.diagnosis
                                        .possible_diagnoses"
                                    :key="'pd-' + idx"
                                    class="border-b pb-4"
                                >
                                    <h3 class="font-semibold text-xl pb-2">
                                        {{ diag.name }}
                                    </h3>
                                    <p class="text-sm text-gray-500 pb-2">
                                        <strong
                                            >{{
                                                t(
                                                    'diagnosisPage.differentiating'
                                                )
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
                                            v-for="(
                                                item, i
                                            ) in diag.supporting_evidence"
                                            :key="'pde-' + i"
                                        >
                                            {{ item }}
                                        </li>
                                    </ul>
                                </div>
                            </CardContent>
                        </Card>

                        <Card
                            v-if="detail.diagnosis?.rule_out?.length"
                            class="shadow-md hover:shadow-lg transition duration-300"
                        >
                            <CardHeader
                                class="bg-muted/20 rounded-t-md px-4 pt-2"
                            >
                                <CardTitle
                                    class="text-lg font-semibold text-red-600"
                                    >❌
                                    {{ t('diagnosisPage.ruleOut') }}</CardTitle
                                >
                            </CardHeader>
                            <CardContent class="space-y-6 px-4 pt-2 pb-4">
                                <div
                                    v-for="(diag, idx) in detail.diagnosis
                                        .rule_out"
                                    :key="'ro-' + idx"
                                    class="border-b pb-4"
                                >
                                    <h3 class="font-semibold text-xl pb-2">
                                        {{ diag.name }}
                                    </h3>
                                    <ul
                                        class="list-disc pl-6 text-sm text-gray-700 dark:text-gray-300 space-y-1 mt-1"
                                    >
                                        <li
                                            v-for="(
                                                item, i
                                            ) in diag.supporting_evidence"
                                            :key="'roe-' + i"
                                        >
                                            {{ item }}
                                        </li>
                                    </ul>
                                </div>
                            </CardContent>
                        </Card>

                        <Card
                            v-if="(detail.further_test || []).length"
                            class="shadow-md hover:shadow-lg transition duration-300"
                        >
                            <CardHeader
                                class="bg-muted/20 rounded-t-md px-4 pt-2"
                            >
                                <CardTitle class="text-lg font-semibold"
                                    >🔬
                                    {{
                                        t('diagnosisPage.furtherTests')
                                    }}</CardTitle
                                >
                            </CardHeader>
                            <CardContent class="space-y-6 px-4 pt-2 pb-4">
                                <div
                                    v-for="(test, idx) in detail.further_test"
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
                                            v-for="(
                                                rel, i
                                            ) in test.related_condition"
                                            :key="'rel-' + i"
                                            class="rounded-md text-xs"
                                            >{{ rel }}</Badge
                                        >
                                    </div>
                                    <p class="text-sm text-red-700 mt-2">
                                        <strong
                                            >{{
                                                t('diagnosisPage.urgency')
                                            }}:</strong
                                        >
                                        {{
                                            test.urgency ||
                                            t('diagnosisPage.routine')
                                        }}
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </template>

                <template v-else-if="view === 'todo'">
                    <h2 class="font-semibold">{{ t('sidebar.todoList') }}</h2>
                    <div class="space-y-2">
                        <label
                            v-for="t in detail.todos"
                            :key="t.text"
                            class="flex items-center gap-2 text-sm"
                        >
                            <Checkbox :checked="t.is_check" disabled />
                            <span>{{ t.text }}</span>
                        </label>
                    </div>
                </template>

                <template v-else-if="view === 'contact'">
                    <div class="flex items-center gap-3">
                        <div class="text-sm text-muted-foreground">
                            {{ t('contact.detail.startChatPrompt') }}
                        </div>
                        <Button @click="goChat">{{
                            t('contact.detail.openChat')
                        }}</Button>
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>
