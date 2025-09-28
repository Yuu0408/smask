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
    };
    return map[value] ? t(`patientForm.options.${map[value]}`) : value;
}

function translateSmoking(value?: string): string {
    if (!value) return t('medicalRecord.notAvailableShort');
    const map: Record<string, string> = {
        never: 'never',
        used_to_quit: 'usedToQuit',
        occasionally: 'occasionally',
        daily: 'daily',
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
              smoking_habit?: string;
              living_situation?: string;
              daily_activity_independence?: string;
              recent_travel_history?: string;
          }
        | undefined;
    if (!d) return [] as Array<{ label: string; value: string }>;
    return [
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
</script>

<template>
    <div class="p-8 space-y-8 overflow-auto">
        <div class="flex items-center gap-3">
            <BookText class="w-8 h-8 text-primary" />
            <h1 class="text-3xl font-bold tracking-tight">
                {{ t('record.title') }}
            </h1>
        </div>
        <div v-if="loading" class="text-muted-foreground animate-pulse">
            {{ t('record.loading') }}
        </div>
        <div v-else-if="!record" class="text-muted-foreground">
            <div class="flex flex-col items-center gap-3 py-10">
                <div class="text-base">{{ t('record.empty') }}</div>
                <Button
                    variant="default"
                    @click="openDialog({ component: MedicalRecordDialog })"
                >
                    {{ t('todo.startConversation') }}
                </Button>
            </div>
        </div>

        <div v-else class="grid gap-8">
            <!-- Reusable info block -->
            <Card>
                <CardHeader>
                    <CardTitle>{{ t('medicalRecord.patientInfo') }}</CardTitle>
                </CardHeader>
                <CardContent>
                    <dl class="divide-y divide-border">
                        <div
                            v-for="item in patientInfoItems"
                            :key="item.label"
                            class="py-3 grid grid-cols-3 gap-4"
                        >
                            <dt
                                class="text-sm font-medium text-muted-foreground"
                            >
                                {{ item.label }}
                            </dt>
                            <dd class="col-span-2 text-sm">{{ item.value }}</dd>
                        </div>
                    </dl>
                </CardContent>
            </Card>

            <Card v-if="obgynItems.length">
                <CardHeader>
                    <CardTitle>{{ t('medicalRecord.obstetric') }}</CardTitle>
                </CardHeader>
                <CardContent>
                    <dl class="divide-y divide-border">
                        <div
                            v-for="item in obgynItems"
                            :key="item.label"
                            class="py-3 grid grid-cols-3 gap-4"
                        >
                            <dt
                                class="text-sm font-medium text-muted-foreground"
                            >
                                {{ item.label }}
                            </dt>
                            <dd class="col-span-2 text-sm">{{ item.value }}</dd>
                        </div>
                    </dl>
                </CardContent>
            </Card>

            <Card v-if="socialItems.length">
                <CardHeader>
                    <CardTitle>{{ t('medicalRecord.socialInfo') }}</CardTitle>
                </CardHeader>
                <CardContent>
                    <dl class="divide-y divide-border">
                        <div
                            v-for="item in socialItems"
                            :key="item.label"
                            class="py-3 grid grid-cols-3 gap-4"
                        >
                            <dt
                                class="text-sm font-medium text-muted-foreground"
                            >
                                {{ item.label }}
                            </dt>
                            <dd class="col-span-2 text-sm">{{ item.value }}</dd>
                        </div>
                    </dl>
                </CardContent>
            </Card>

            <Card v-if="medicalHistoryItems.length">
                <CardHeader>
                    <CardTitle>{{
                        t('medicalRecord.medicalHistory')
                    }}</CardTitle>
                </CardHeader>
                <CardContent>
                    <dl class="divide-y divide-border">
                        <div
                            v-for="item in medicalHistoryItems"
                            :key="item.label"
                            class="py-3 grid grid-cols-3 gap-4"
                        >
                            <dt
                                class="text-sm font-medium text-muted-foreground"
                            >
                                {{ item.label }}
                            </dt>
                            <dd class="col-span-2 text-sm">{{ item.value }}</dd>
                        </div>
                    </dl>
                </CardContent>
            </Card>
            <div class="flex justify-end">
                <Button
                    @click="
                        openDialog({
                            component: SendContactDialog,
                            props: { recordId: record?.record_id },
                        })
                    "
                >
                    {{ t('record.send') }}
                </Button>
            </div>
        </div>
    </div>
</template>
