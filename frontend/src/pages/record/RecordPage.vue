<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';
import { useChatStore } from '@/stores/record';
import type { GetCurrentRecordResponse } from '@/types/medical-record';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import SendContactDialog from '@/pages/record/SendContactDialog.vue';
import { useI18n } from 'vue-i18n';
import { BookText } from 'lucide-vue-next';

const { user } = storeToRefs(useAuthStore());
const { t, locale } = useI18n();
const userId = computed(() => user.value?.id ?? '');
const recordId = computed(() => user.value?.currentRecordId ?? '');

const chatStore = useChatStore();
const { openDialog } = useDialog();
const record = ref<GetCurrentRecordResponse | null>(null);
const loading = ref(false);

onMounted(async () => {
    if (!userId.value || !recordId.value) return;
    loading.value = true;
    try {
        record.value = await chatStore.getCurrentRecord({
            user_id: userId.value,
            record_id: recordId.value,
        });
    } finally {
        loading.value = false;
    }
});

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

function formatDateTime(dateStr?: string | null): string {
    if (!dateStr) return t('medicalRecord.notAvailableShort');
    const date = new Date(dateStr);
    const loc = locale.value === 'vi' ? 'vi-VN' : 'en-US';
    return date.toLocaleString(loc, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
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
    const d = record.value?.data?.patient_info;
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

const patientName = computed(
    () =>
        record.value?.data?.patient_info?.full_name ||
        t('medicalRecord.notAvailableShort')
);

const chiefComplaint = computed(
    () =>
        record.value?.data?.medical_history?.chief_complaint ||
        t('history.noMessagesYet')
);

const symptomProgression = computed(
    () =>
        record.value?.data?.medical_history?.medical_history ||
        t('medicalRecord.notAvailableShort')
);

const recordMeta = computed(() => ({
    created: formatDateTime(record.value?.created_at),
    updated: formatDateTime(record.value?.updated_at),
}));

const obgynItems = computed(() => {
    const d = record.value?.data?.obstetric_gynecological_history as
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

const socialItems = computed(() => {
    const d = record.value?.data?.social_information as
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

    // Append details if present
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
            desc = `${t('patientForm.smokingDetails.startAge')}: ${sd.start_age ?? '-'} \u001a ${t('patientForm.smokingDetails.endAge')}: ${sd.end_age ?? '-'}${years != null ? ` (~${years})` : ''}, ${t('patientForm.smokingDetails.cigarettesPerDay')}: ${sd.cigarettes_per_day ?? '-'}`;
        } else if (d.smoking_habit === 'current') {
            desc = `${t('patientForm.smokingDetails.startAge')}: ${sd.start_age ?? '-'} \u001a now, ${t('patientForm.smokingDetails.cigarettesPerDay')}: ${sd.cigarettes_per_day ?? '-'}`;
        }
        items.splice(3, 0, { label: t('medicalRecord.smoking'), value: desc });
    }
    return items;
});

const medicalHistoryItems = computed(() => {
    const d = record.value?.data?.medical_history as
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
            <div
                class="relative h-full min-h-0 w-full flex flex-col overflow-hidden"
            >
                <div class="flex-1 min-h-0 overflow-y-auto">
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
                                    <BookText class="size-4" />
                                    {{ t('record.title') }}
                                </div>
                                <div class="space-y-1">
                                    <h1
                                        class="text-3xl font-bold tracking-tight text-foreground"
                                    >
                                        {{ patientName }}
                                    </h1>
                                </div>
                                <div
                                    class="flex flex-wrap gap-3 text-xs text-muted-foreground"
                                >
                                    <span
                                        class="inline-flex items-center gap-2 rounded-full bg-white/80 px-3 py-1 shadow-sm shadow-primary/20 backdrop-blur"
                                    >
                                        <span
                                            class="size-2 rounded-full bg-primary"
                                        ></span>
                                        {{ t('record.meta.created') }}:
                                        <span
                                            class="font-medium text-foreground"
                                        >
                                            {{ recordMeta.created }}
                                        </span>
                                    </span>
                                    <span
                                        class="inline-flex items-center gap-2 rounded-full bg-white/80 px-3 py-1 shadow-sm shadow-primary/20 backdrop-blur"
                                    >
                                        <BookText
                                            class="h-4 w-4 text-primary"
                                        />
                                        {{ t('record.meta.updated') }}:
                                        <span
                                            class="font-medium text-foreground"
                                        >
                                            {{ recordMeta.updated }}
                                        </span>
                                    </span>
                                </div>
                            </div>
                        </header>

                        <div
                            v-if="loading"
                            class="text-muted-foreground animate-pulse"
                        >
                            {{ t('record.loading') }}
                        </div>

                        <div v-else-if="!record" class="text-muted-foreground">
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
                                        {{ t('record.empty') }}
                                    </p>
                                    <Button
                                        variant="default"
                                        class="rounded-xl shadow-md shadow-primary/20"
                                        @click="
                                            openDialog({
                                                component: MedicalRecordDialog,
                                            })
                                        "
                                    >
                                        {{ t('todo.startConversation') }}
                                    </Button>
                                </div>
                            </div>
                        </div>

                        <div
                            v-else
                            class="grid gap-6 lg:grid-cols-[1.25fr_0.95fr] lg:items-start"
                        >
                            <div class="space-y-6">
                                <Card
                                    class="overflow-hidden border-0 bg-gradient-to-br from-primary/20 via-white to-accent/10 shadow-xl shadow-primary/20"
                                >
                                    <CardHeader class="space-y-1">
                                        <CardTitle
                                            class="text-lg font-semibold text-primary"
                                        >
                                            {{
                                                t(
                                                    'medicalRecord.chiefComplaint'
                                                )
                                            }}
                                        </CardTitle>
                                        <p
                                            class="text-sm text-muted-foreground"
                                        >
                                            {{ t('record.meta.updated') }}:
                                            {{ recordMeta.updated }}
                                        </p>
                                    </CardHeader>
                                    <CardContent
                                        class="space-y-3 text-foreground"
                                    >
                                        <p
                                            class="text-base leading-relaxed font-medium"
                                        >
                                            {{ chiefComplaint }}
                                        </p>
                                        <div
                                            class="rounded-2xl bg-white/70 px-4 py-3 text-sm shadow-inner shadow-primary/10"
                                        >
                                            <div
                                                class="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground mb-1"
                                            >
                                                {{
                                                    t(
                                                        'medicalRecord.symptomProgression'
                                                    )
                                                }}
                                            </div>
                                            <p
                                                class="leading-relaxed text-muted-foreground"
                                            >
                                                {{ symptomProgression }}
                                            </p>
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card
                                    v-if="socialItems.length"
                                    class="shadow-lg shadow-primary/10"
                                >
                                    <CardHeader>
                                        <CardTitle>{{
                                            t('medicalRecord.socialInfo')
                                        }}</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <dl class="divide-y divide-border/70">
                                            <div
                                                v-for="item in socialItems"
                                                :key="item.label"
                                                class="grid grid-cols-3 gap-4 py-3"
                                            >
                                                <dt
                                                    class="text-sm font-medium text-muted-foreground"
                                                >
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
                                    v-if="medicalHistoryItems.length"
                                    class="shadow-lg shadow-primary/10"
                                >
                                    <CardHeader>
                                        <CardTitle>{{
                                            t('medicalRecord.medicalHistory')
                                        }}</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <dl class="divide-y divide-border/70">
                                            <div
                                                v-for="item in medicalHistoryItems"
                                                :key="item.label"
                                                class="grid grid-cols-3 gap-4 py-3"
                                            >
                                                <dt
                                                    class="text-sm font-medium text-muted-foreground"
                                                >
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
                                    v-if="obgynItems.length"
                                    class="shadow-lg shadow-primary/10"
                                >
                                    <CardHeader>
                                        <CardTitle>{{
                                            t('medicalRecord.obstetric')
                                        }}</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <dl class="divide-y divide-border/70">
                                            <div
                                                v-for="item in obgynItems"
                                                :key="item.label"
                                                class="grid grid-cols-3 gap-4 py-3"
                                            >
                                                <dt
                                                    class="text-sm font-medium text-muted-foreground"
                                                >
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
                                class="space-y-4 lg:sticky lg:top-24 lg:self-start lg:w-full lg:max-w-md lg:transition-all lg:duration-700 lg:ease-out lg:delay-75"
                            >
                                <div class="space-y-4">
                                    <Card class="shadow-lg shadow-primary/10">
                                        <CardHeader>
                                            <CardTitle>{{
                                                t('medicalRecord.patientInfo')
                                            }}</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <dl
                                                class="divide-y divide-border/70"
                                            >
                                                <div
                                                    v-for="item in patientInfoItems"
                                                    :key="item.label"
                                                    class="grid grid-cols-3 gap-4 py-3"
                                                >
                                                    <dt
                                                        class="text-sm font-medium text-muted-foreground"
                                                    >
                                                        {{ item.label }}
                                                    </dt>
                                                    <dd
                                                        class="col-span-2 text-sm"
                                                    >
                                                        {{ item.value }}
                                                    </dd>
                                                </div>
                                            </dl>
                                        </CardContent>
                                    </Card>
                                    <Button
                                        class="w-full rounded-xl shadow-lg shadow-primary/20"
                                        :disabled="!record"
                                        @click="
                                            openDialog({
                                                component: SendContactDialog,
                                                props: {
                                                    recordId: record?.record_id,
                                                },
                                            })
                                        "
                                    >
                                        {{ t('record.send') }}
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
