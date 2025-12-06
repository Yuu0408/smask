<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useContactStore } from '@/stores/contact';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import ChatMessage from '@/components/ChatMessage.vue';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
import {
    ListTodo,
    Stethoscope,
    ClipboardCheck,
    AlertTriangle,
    TestTubes,
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const contact = useContactStore();
const { user } = storeToRefs(useAuthStore());
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
    const selfRole = user.value?.role === 'doctor' ? 'doctor' : 'patient';
    if (role === 'human') return 'human';
    if (role === 'ai' || role === 'system') return 'ai';
    if (role === selfRole) return 'human';
    return 'ai';
}

const selfLabel = computed(() => user.value?.username || 'You');
const otherLabel = computed(() => {
    if (user.value?.role === 'doctor') {
        return (
            detail.value?.medical_record?.patient_info?.full_name || 'Patient'
        );
    }
    if (user.value?.role === 'patient') {
        return detail.value?.doctor_username || 'Doctor';
    }
    return detail.value?.medical_record?.patient_info?.full_name || 'Contact';
});

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

const chiefComplaint = computed(
    () =>
        detail.value?.medical_record?.medical_history?.chief_complaint ||
        t('history.noMessagesYet')
);
const symptomProgression = computed(
    () =>
        detail.value?.medical_record?.medical_history?.medical_history ||
        t('medicalRecord.notAvailableShort')
);

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
              past_medical_history?: string;
              current_medications?: string;
              allergies?: string;
              family_medical_history?: string;
          }
        | undefined;
    if (!d) return [] as Array<{ label: string; value: string }>;
    return [
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

const todoItems = computed(() => detail.value?.todos || []);
const completedTodos = computed(
    () => todoItems.value.filter((t: any) => t.is_check).length
);
const pendingTodos = computed(
    () => (todoItems.value.length ?? 0) - completedTodos.value
);
const completionPct = computed(() => {
    const total = todoItems.value.length ?? 0;
    if (!total) return 0;
    return Math.round((completedTodos.value / total) * 100);
});

function urgencyBadgeClass(urgency?: string | null) {
    if (!urgency) return 'bg-primary/10 text-primary';
    const lower = urgency.toLowerCase();
    if (lower.includes('urgent') || lower.includes('emerg') || lower.includes('stat')) {
        return 'bg-red-100 text-red-700 ring-1 ring-red-200';
    }
    if (lower.includes('high')) {
        return 'bg-amber-100 text-amber-700 ring-1 ring-amber-200';
    }
    return 'bg-primary/10 text-primary';
}
</script>

<template>
    <div
        v-if="!loading && detail"
        class="flex min-h-[calc(100vh-4rem)] h-[calc(100vh-4rem)] flex-col overflow-hidden"
    >
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
                    class="mx-auto w-full max-w-6xl p-6 space-y-6 mb-10"
                >
                <template v-if="view === 'record'">
                    <div
                        class="grid gap-6 lg:grid-cols-[2fr_1fr] lg:items-start"
                    >
                        <div class="space-y-6">
                            <Card
                                class="overflow-hidden border-0 bg-gradient-to-br from-primary/20 via-white to-accent/10 shadow-xl shadow-primary/20"
                            >
                                <CardHeader class="space-y-1">
                                    <CardTitle
                                        class="text-lg font-semibold text-primary"
                                    >
                                        {{ t('medicalRecord.chiefComplaint') }}
                                    </CardTitle>
                                    <p class="text-sm text-muted-foreground">
                                        {{ t('record.meta.updated') }}:
                                        {{
                                            detail.medical_record?.updated_at
                                                ? formatDate(
                                                      detail.medical_record
                                                          ?.updated_at
                                                  )
                                                : t('medicalRecord.notAvailableShort')
                                        }}
                                    </p>
                                </CardHeader>
                                <CardContent class="space-y-3 text-foreground">
                                    <p class="text-base leading-relaxed font-medium">
                                        {{ chiefComplaint }}
                                    </p>
                                    <div
                                        class="rounded-2xl bg-white/70 px-4 py-3 text-sm shadow-inner shadow-primary/10"
                                    >
                                        <div
                                            class="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground mb-1"
                                        >
                                            {{ t('medicalRecord.symptomProgression') }}
                                        </div>
                                        <p class="leading-relaxed text-muted-foreground">
                                            {{ symptomProgression }}
                                        </p>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card class="shadow-lg shadow-primary/10 border border-primary/10">
                                <CardHeader>
                                    <CardTitle>{{
                                        t('medicalRecord.medicalHistory')
                                    }}</CardTitle>
                                </CardHeader>
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

                            <Card class="shadow-lg shadow-primary/10 border border-primary/10">
                                <CardHeader>
                                    <CardTitle>{{
                                        t('medicalRecord.socialInfo')
                                    }}</CardTitle>
                                </CardHeader>
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
                                class="shadow-lg shadow-primary/10 border border-primary/10"
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
                        </div>

                        <div
                            class="space-y-4 lg:sticky lg:top-24 lg:self-start lg:w-full lg:max-w-md lg:transition-all lg:duration-500 lg:ease-out"
                        >
                            <Card class="shadow-lg shadow-primary/10 border border-primary/10">
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
                            <Button
                                class="w-full rounded-xl shadow-lg shadow-primary/20"
                                @click="goChat"
                            >
                                {{ t('contact.detail.openChat') }}
                            </Button>
                        </div>
                    </div>
                </template>

                <template v-else-if="view === 'conversation'">
                    <h2 class="font-semibold">Conversation Snapshot</h2>
                    <div class="space-y-2">
                        <ChatMessage
                            v-for="m in detail.conversation || []"
                            :key="m.id"
                            :role="roleForMessage(m.role)"
                            :content="m.content"
                            :human-label="selfLabel"
                            :ai-label="otherLabel"
                        />
                    </div>
                </template>

                <template v-else-if="view === 'diagnosis'">
                    <div class="space-y-6 mb-4">
                        <div
                            class="overflow-hidden rounded-3xl border border-primary/15 bg-gradient-to-r from-primary/10 via-white to-accent/10 p-6 shadow-lg shadow-primary/20"
                        >
                            <div
                                class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between"
                            >
                                <div class="space-y-1">
                                    <div
                                        class="inline-flex items-center gap-2 rounded-full bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-primary shadow-inner shadow-primary/10"
                                    >
                                        <Stethoscope class="size-4" />
                                        {{ t('sidebar.diagnosis') }}
                                    </div>
                                    <h2 class="text-2xl font-bold text-foreground">
                                        {{ t('diagnosisPage.title') }}
                                    </h2>
                                    <p class="text-sm text-muted-foreground">
                                        {{
                                            detail.reasoning_process
                                                ? t('diagnosisPage.reasoning')
                                                : t('diagnosisPage.notAvailable')
                                        }}
                                    </p>
                                </div>
                                <div class="flex gap-3">
                                    <div
                                        class="rounded-2xl border border-primary/20 bg-white/70 px-4 py-3 text-sm shadow-sm"
                                    >
                                        <p class="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                                            {{ t('diagnosisPage.mostLikely') }}
                                        </p>
                                        <p class="font-semibold text-primary">
                                            {{
                                                detail.diagnosis?.most_likely?.name ||
                                                t('diagnosisPage.notAvailableShort')
                                            }}
                                        </p>
                                    </div>
                                    <div
                                        class="rounded-2xl border border-primary/20 bg-white/70 px-4 py-3 text-sm shadow-sm"
                                    >
                                        <p class="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                                            {{ t('diagnosisPage.furtherTests') }}
                                        </p>
                                        <p class="font-semibold text-primary">
                                            {{
                                                (detail.further_test || []).length ||
                                                t('diagnosisPage.notAvailableShort')
                                            }}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="grid gap-6 lg:grid-cols-2">
                            <Card
                                v-if="detail.reasoning_process"
                                class="lg:col-span-2 overflow-hidden border border-primary/10 shadow-lg shadow-primary/15 bg-white/80 backdrop-blur"
                            >
                                <CardHeader class="bg-white/80 backdrop-blur flex items-center gap-3">
                                    <ClipboardCheck class="size-5 text-primary" />
                                    <CardTitle class="text-lg font-semibold text-primary">
                                        {{ t('diagnosisPage.reasoning') }}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div class="pr-1 text-sm leading-relaxed text-foreground/80">
                                        {{ detail.reasoning_process }}
                                    </div>
                                </CardContent>
                            </Card>

                            <Card
                                v-if="detail.diagnosis?.most_likely"
                                class="overflow-hidden border border-primary/10 shadow-lg shadow-primary/20 bg-gradient-to-br from-primary/15 via-white to-primary/5 backdrop-blur"
                            >
                                <CardHeader class="bg-white/80 backdrop-blur flex items-center gap-3">
                                    <AlertTriangle class="size-5 text-primary" />
                                    <CardTitle class="text-lg font-semibold text-primary">
                                        {{ t('diagnosisPage.mostLikely') }}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent class="flex h-full flex-col gap-4 justify-start items-center text-left min-h-[360px] px-6">
                                    <div class="w-full max-w-2xl space-y-3 mx-auto">
                                        <h3 class="text-xl font-semibold text-foreground leading-tight">
                                            {{ detail.diagnosis.most_likely.name }}
                                        </h3>
                                        <p class="text-sm text-foreground/80 leading-relaxed">
                                            <strong>{{ t('diagnosisPage.differentiating') }}:</strong>
                                            {{
                                                detail.diagnosis.most_likely
                                                    .differentiating_factor ||
                                                t('diagnosisPage.notAvailableShort')
                                            }}
                                        </p>
                                        <div class="space-y-2">
                                            <p class="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                                                {{ t('diagnosisPage.supporting') }}
                                            </p>
                                            <ul class="space-y-2 text-sm text-foreground">
                                                <li
                                                    v-for="(item, idx) in detail.diagnosis
                                                        .most_likely.supporting_evidence"
                                                    :key="'ml-' + idx"
                                                    class="rounded-xl bg-white/80 px-3 py-2 shadow-inner shadow-primary/10 ring-1 ring-primary/5"
                                                >
                                                    {{ item }}
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card
                                v-if="detail.diagnosis?.possible_diagnoses?.length"
                                class="overflow-hidden border border-primary/10 shadow-lg shadow-primary/15 bg-white/80 backdrop-blur"
                            >
                                <CardHeader class="bg-white/80 backdrop-blur flex items-center gap-3">
                                    <ClipboardCheck class="size-5 text-primary" />
                                    <CardTitle class="text-lg font-semibold text-primary">
                                        {{ t('diagnosisPage.possible') }}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent class="flex h-full w-full flex-col gap-4 px-6 min-h-[360px] justify-start items-center text-left">
                                    <div
                                        v-for="(diag, idx) in detail.diagnosis
                                            .possible_diagnoses"
                                        :key="'pd-' + idx"
                                        class="rounded-2xl border border-primary/10 bg-white/85 p-4 shadow-sm space-y-2 w-full max-w-2xl mx-auto"
                                    >
                                        <h3 class="font-semibold text-lg leading-tight">{{ diag.name }}</h3>
                                        <p class="text-sm text-foreground/80 leading-relaxed">
                                            <strong>{{ t('diagnosisPage.differentiating') }}:</strong>
                                            {{
                                                diag.differentiating_factor ||
                                                t('diagnosisPage.notAvailableShort')
                                            }}
                                        </p>
                                        <p class="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground mt-1">
                                            {{ t('diagnosisPage.supporting') }}
                                        </p>
                                        <ul class="list-disc pl-5 text-sm text-foreground space-y-1">
                                            <li
                                                v-for="(item, i) in diag.supporting_evidence"
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
                                class="overflow-hidden border border-primary/10 shadow-lg shadow-primary/15 bg-white/80 backdrop-blur"
                            >
                                <CardHeader class="bg-white/80 backdrop-blur flex items-center gap-3">
                                    <AlertTriangle class="size-5 text-primary" />
                                    <CardTitle class="text-lg font-semibold text-primary">
                                        {{ t('diagnosisPage.ruleOut') }}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent class="flex h-full w-full flex-col gap-3 px-6 min-h-[340px] justify-start items-center text-left">
                                    <div
                                        v-for="(diag, idx) in detail.diagnosis
                                            .rule_out"
                                        :key="'ro-' + idx"
                                        class="rounded-2xl border border-primary/10 bg-white/85 p-4 shadow-sm space-y-2 w-full max-w-2xl mx-auto"
                                    >
                                        <h3 class="font-semibold text-lg leading-tight">{{ diag.name }}</h3>
                                        <ul class="list-disc pl-5 text-sm text-foreground space-y-1 mt-1">
                                            <li
                                                v-for="(item, i) in diag.supporting_evidence"
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
                                class="overflow-hidden border border-primary/10 shadow-lg shadow-primary/15 bg-white/80 backdrop-blur"
                            >
                                <CardHeader class="bg-white/80 backdrop-blur flex items-center gap-3">
                                    <TestTubes class="size-5 text-primary" />
                                    <CardTitle class="text-lg font-semibold text-primary">
                                        {{ t('diagnosisPage.furtherTests') }}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent class="flex h-full w-full flex-col gap-3 px-6 min-h-[360px] justify-start items-center text-left">
                                    <div
                                        v-for="(test, idx) in detail.further_test"
                                        :key="'test-' + idx"
                                        class="rounded-2xl border border-primary/10 bg-white/85 p-4 shadow-sm space-y-2 w-full max-w-2xl mx-auto"
                                    >
                                        <div class="flex items-start justify-between gap-2">
                                            <div>
                                                <h3 class="font-semibold text-lg leading-tight">
                                                    {{ test.name }}
                                                </h3>
                                                <p class="text-sm text-foreground/80 mt-1 leading-relaxed">
                                                    {{ test.purpose }}
                                                </p>
                                            </div>
                                            <span
                                                class="rounded-full px-3 py-1 text-xs font-semibold"
                                                :class="urgencyBadgeClass(test.urgency)"
                                            >
                                                {{
                                                    test.urgency ||
                                                    t('diagnosisPage.routine')
                                                }}
                                            </span>
                                        </div>
                                        <div class="mt-3 flex flex-wrap gap-2">
                                            <Badge
                                                v-for="(rel, i) in test.related_condition"
                                                :key="'rel-' + i"
                                                class="rounded-md text-xs"
                                                >{{ rel }}</Badge
                                            >
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </template>

                <template v-else-if="view === 'todo'">
                    <div class="space-y-5">
                        <div class="grid gap-4 sm:grid-cols-3">
                            <Card class="shadow-lg shadow-primary/10">
                                <CardHeader class="space-y-1">
                                    <CardTitle class="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                                        {{ t('sidebar.todoList') }}
                                    </CardTitle>
                                    <p class="text-sm text-muted-foreground">
                                        {{ t('todo.title') }}
                                    </p>
                                </CardHeader>
                                <CardContent>
                                    <div class="text-2xl font-bold text-foreground">
                                        {{ pendingTodos }}
                                    </div>
                                    <p class="text-xs text-muted-foreground">
                                        Pending
                                    </p>
                                </CardContent>
                            </Card>
                            <Card class="shadow-lg shadow-primary/10">
                                <CardHeader class="space-y-1">
                                    <CardTitle class="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                                        {{ t('common.done') }}
                                    </CardTitle>
                                    <p class="text-sm text-muted-foreground">
                                        {{ t('todo.items') }}
                                    </p>
                                </CardHeader>
                                <CardContent>
                                    <div class="text-2xl font-bold text-foreground">
                                        {{ completedTodos }}
                                    </div>
                                    <p class="text-xs text-muted-foreground">
                                        Completed
                                    </p>
                                </CardContent>
                            </Card>
                            <Card class="shadow-lg shadow-primary/10">
                                <CardHeader class="space-y-2">
                                    <CardTitle class="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                                        Progress
                                    </CardTitle>
                                    <p class="text-sm text-muted-foreground">
                                        {{ t('sidebar.todoList') }}
                                    </p>
                                </CardHeader>
                                <CardContent>
                                    <div class="text-2xl font-bold text-foreground">
                                        {{ completionPct }}%
                                    </div>
                                    <div class="mt-2 h-2 w-full overflow-hidden rounded-full bg-muted">
                                        <div
                                            class="h-full rounded-full bg-primary transition-all duration-500"
                                            :style="{ width: `${completionPct}%` }"
                                        ></div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                        <Card class="shadow-lg shadow-primary/10 border border-primary/10">
                            <CardHeader class="flex items-center justify-between">
                                <CardTitle>{{ t('todo.upcomingActions') }}</CardTitle>
                                <div class="inline-flex items-center gap-2 text-sm text-muted-foreground">
                                    <ListTodo class="size-4" />
                                    {{ todoItems.length }} {{ t('todo.items') }}
                                </div>
                            </CardHeader>
                            <CardContent class="space-y-3">
                                <label
                                    v-for="t in todoItems"
                                    :key="t.text"
                                    class="flex items-center gap-3 rounded-2xl border border-border/70 bg-white/70 p-3 text-sm shadow-sm"
                                >
                                    <Checkbox :checked="t.is_check" disabled />
                                    <span
                                        :class="t.is_check ? 'line-through text-muted-foreground' : ''"
                                        >{{ t.text }}</span
                                    >
                                </label>
                            </CardContent>
                        </Card>
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
</div>
</template>
