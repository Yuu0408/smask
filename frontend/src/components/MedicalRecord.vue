<script setup lang="ts">
// @ts-nocheck
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import CardSection from './CardSection.vue';
import Info from './Info.vue';
import { useI18n } from 'vue-i18n';

// Legacy component; data wiring disabled
const router = useRouter();
const record = computed(() => null);
const { t, locale } = useI18n();

onMounted(() => {
    if (!record.value) router.push('/chat');
});

function formatDate(dateStr: string): string {
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
</script>

<template>
    <div
        class="max-w-3xl w-full mx-auto px-6 pt-6 pb-12 space-y-8"
        v-if="record"
    >
        <h1 class="text-3xl font-bold text-center mb-8">
            {{ t('medicalRecord.title') }}
        </h1>

        <CardSection :title="t('medicalRecord.patientInfo')">
            <Info
                :label="t('medicalRecord.fullName')"
                :value="record.patient_info.full_name"
            />
            <Info
                :label="t('medicalRecord.birthday')"
                :value="formatDate(record.patient_info.birthday)"
            />
            <Info
                :label="t('medicalRecord.gender')"
                :value="translateGender(record.patient_info.gender)"
            />
            <Info
                :label="t('medicalRecord.occupation')"
                :value="record.patient_info.occupation"
            />
            <Info
                :label="t('medicalRecord.nationality')"
                :value="record.patient_info.nationality"
            />
            <Info
                :label="t('medicalRecord.address')"
                :value="record.patient_info.address"
            />
        </CardSection>

        <CardSection :title="t('medicalRecord.medicalHistory')">
            <Info
                :label="t('medicalRecord.chiefComplaint')"
                :value="record.medical_history.chief_complaint"
            />
            <Info
                :label="t('medicalRecord.symptomProgression')"
                :value="record.medical_history.medical_history"
            />
            <Info
                :label="t('medicalRecord.pastMedicalHistory')"
                :value="record.medical_history.past_medical_history"
            />
            <Info
                :label="t('medicalRecord.currentMedications')"
                :value="
                    record.medical_history.current_medications ||
                    t('medicalRecord.none')
                "
            />
            <Info
                :label="t('medicalRecord.allergies')"
                :value="
                    record.medical_history.allergies || t('medicalRecord.none')
                "
            />
            <Info
                :label="t('medicalRecord.familyHistory')"
                :value="record.medical_history.family_medical_history"
            />
        </CardSection>

        <CardSection :title="t('medicalRecord.socialInfo')">
            <Info
                :label="t('medicalRecord.alcohol')"
                :value="
                    translateAlcohol(
                        record.social_information.alcohol_consumption
                    )
                "
            />
            <Info
                :label="t('medicalRecord.smoking')"
                :value="
                    translateSmoking(record.social_information.smoking_habit)
                "
            />
            <Info
                :label="t('medicalRecord.livingSituation')"
                :value="
                    translateLivingSituation(
                        record.social_information.living_situation
                    )
                "
            />
            <Info
                :label="t('medicalRecord.dailyActivity')"
                :value="
                    translateDailyIndependence(
                        record.social_information.daily_activity_independence
                    )
                "
            />
            <Info
                :label="t('medicalRecord.travelHistory')"
                :value="
                    translateTravel(
                        record.social_information.recent_travel_history
                    )
                "
            />
        </CardSection>

        <CardSection
            v-if="record.obstetric_gynecological_history"
            :title="t('medicalRecord.obstetric')"
        >
            <Info
                :label="t('medicalRecord.menstruationStatus')"
                :value="
                    record.obstetric_gynecological_history
                        ?.menstruation_status ||
                    t('medicalRecord.notAvailableShort')
                "
            />
            <Info
                :label="t('medicalRecord.menstrualCycle')"
                :value="
                    record.obstetric_gynecological_history?.menstrual_cycle ||
                    t('medicalRecord.notAvailableShort')
                "
            />
            <Info
                :label="t('medicalRecord.sexualActivity')"
                :value="
                    record.obstetric_gynecological_history
                        ?.recent_sexual_activity != null
                        ? record.obstetric_gynecological_history
                              .recent_sexual_activity
                            ? t('medicalRecord.yes')
                            : t('medicalRecord.no')
                        : t('medicalRecord.notAvailableShort')
                "
            />
        </CardSection>
    </div>
</template>
