<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import CardSection from './CardSection.vue';
import Info from './Info.vue';
import { useI18n } from 'vue-i18n';

const store = useUserStore();
const router = useRouter();
const record = computed(() => store.medicalRecord);
const { t } = useI18n();

onMounted(() => {
    if (!record.value) router.push('/chat');
});

function formatDate(dateStr: string): string {
    if (!dateStr) return t('medicalRecord.notAvailableShort');
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });
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
                :value="record.patient_info.gender"
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
                    record.social_information.alcohol_consumption ||
                    t('medicalRecord.notAvailableShort')
                "
            />
            <Info
                :label="t('medicalRecord.smoking')"
                :value="
                    record.social_information.smoking_habit ||
                    t('medicalRecord.notAvailableShort')
                "
            />
            <Info
                :label="t('medicalRecord.livingSituation')"
                :value="
                    record.social_information.living_situation ||
                    t('medicalRecord.notAvailableShort')
                "
            />
            <Info
                :label="t('medicalRecord.dailyActivity')"
                :value="
                    record.social_information.daily_activity_independence ||
                    t('medicalRecord.notAvailableShort')
                "
            />
            <Info
                :label="t('medicalRecord.travelHistory')"
                :value="
                    record.social_information.recent_travel_history ||
                    t('medicalRecord.notAvailableShort')
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
