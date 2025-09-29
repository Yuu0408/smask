<script setup lang="ts">
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { toast } from 'vue-sonner';
import { Check, Loader2 } from 'lucide-vue-next';

import { toTypedSchema } from '@vee-validate/zod';
import { useForm } from 'vee-validate';
import z from 'zod';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

import { FormField } from '@/components/ui/form';
import FormItem from '@/components/ui/form/FormItem.vue';
import FormLabel from '@/components/ui/form/FormLabel.vue';
import FormControl from '@/components/ui/form/FormControl.vue';
import FormMessage from '@/components/ui/form/FormMessage.vue';

import {
    Select,
    SelectTrigger,
    SelectContent,
    SelectItem,
    SelectValue,
} from '@/components/ui/select';

import { useChatStore } from '@/stores/chat';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import VoiceCallDialog from '@/pages/chat/voice/VoiceCallDialog.vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';

const { closeAllDialogs, openDialog } = useDialog();
const { t } = useI18n();
const props = defineProps<{ mode?: 'chat' | 'voice' }>();
const emits = defineEmits<{
    (e: 'submit', payload: any): void;
}>();
const router = useRouter();

const chatStore = useChatStore();
const authStore = useAuthStore();
const loading = ref({ submit: false });

const { user } = storeToRefs(authStore);
console.log('current user in MedicalRecordForm:', user.value);
const userId = computed(() => user.value?.id ?? '');

// Helper computed to estimate years smoked for UI hint
// Initialized after form below to access form.values

/**
 * Schema
 * - Core required fields mirror your original isFormValid()
 * - Female-specific fields become required when gender === 'Female'
 * - recent_sexual_activity is tri-state (null | true | false) and required for Female
 */
const baseRequired = {
    full_name: z.string().min(1, t('patientForm.validation.required')),
    birthday: z.string().min(1, t('patientForm.validation.required')),
    gender: z.enum(['Male', 'Female', 'Other'], {
        required_error: t('patientForm.validation.required'),
    }),
    occupation: z.string().min(1, t('patientForm.validation.required')),
    nationality: z.string().min(1, t('patientForm.validation.required')),
    address: z.string().min(1, t('patientForm.validation.required')),

    chief_complaint: z.string().min(1, t('patientForm.validation.required')),
    medical_history: z.string().min(1, t('patientForm.validation.required')),
    past_medical_history: z
        .string()
        .min(1, t('patientForm.validation.required')),
    current_medications: z
        .string()
        .min(1, t('patientForm.validation.required')),
    allergies: z.string().min(1, t('patientForm.validation.required')),
    family_medical_history: z
        .string()
        .min(1, t('patientForm.validation.required')),

    alcohol_consumption: z
        .string()
        .min(1, t('patientForm.validation.required')),
    // alcohol detail fields (as strings; coerced on submit)
    alcohol_per_month_times: z.string().optional(),
    alcohol_per_week_times: z.string().optional(),
    alcohol_per_time_ml: z.string().optional(),
    alcohol_avg_per_day_ml: z.string().optional(),
    alcohol_drink_type: z.string().optional(),

    smoking_habit: z.string().min(1, t('patientForm.validation.required')),
    // smoking detail fields
    smoking_start_age: z.string().optional(),
    smoking_end_age: z.string().optional(),
    smoking_cigarettes_per_day: z.string().optional(),
    living_situation: z.string().min(1, t('patientForm.validation.required')),
    daily_activity_independence: z
        .string()
        .min(1, t('patientForm.validation.required')),
    recent_travel_history: z
        .string()
        .min(1, t('patientForm.validation.required')),

    // Female-only (conditional)
    menstruation_status: z.string().optional(),
    menstrual_cycle: z.string().optional(),
    recent_sexual_activity: z.preprocess(
        (v) => (v === 'true' ? true : v === 'false' ? false : null),
        z.boolean().nullable()
    ),
};

const rawSchema = z.object(baseRequired).superRefine((val, ctx) => {
    if (val.gender === 'Female') {
        if (!val.menstruation_status || val.menstruation_status.trim() === '') {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['menstruation_status'],
                message: t('patientForm.validation.required'),
            });
        }
        if (!val.menstrual_cycle || val.menstrual_cycle.trim() === '') {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['menstrual_cycle'],
                message: t('patientForm.validation.required'),
            });
        }
        if (
            val.recent_sexual_activity === null ||
            val.recent_sexual_activity === undefined
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['recent_sexual_activity'],
                message: t('patientForm.validation.required'),
            });
        }
    }
    // Alcohol conditional requirements
    const num = (s?: string | null) => (s && s.trim() !== '' ? Number(s) : NaN);
    if (val.alcohol_consumption === 'occasionally') {
        if (
            !val.alcohol_per_month_times ||
            isNaN(num(val.alcohol_per_month_times)) ||
            num(val.alcohol_per_month_times) <= 0
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['alcohol_per_month_times'],
                message: t('patientForm.validation.required'),
            });
        }
        if (
            !val.alcohol_per_time_ml ||
            isNaN(num(val.alcohol_per_time_ml)) ||
            num(val.alcohol_per_time_ml) <= 0
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['alcohol_per_time_ml'],
                message: t('patientForm.validation.required'),
            });
        }
        if (!val.alcohol_drink_type || val.alcohol_drink_type.trim() === '') {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['alcohol_drink_type'],
                message: t('patientForm.validation.required'),
            });
        }
    }
    if (val.alcohol_consumption === 'frequently') {
        if (
            !val.alcohol_per_week_times ||
            isNaN(num(val.alcohol_per_week_times)) ||
            num(val.alcohol_per_week_times) <= 0
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['alcohol_per_week_times'],
                message: t('patientForm.validation.required'),
            });
        }
        if (
            !val.alcohol_avg_per_day_ml ||
            isNaN(num(val.alcohol_avg_per_day_ml)) ||
            num(val.alcohol_avg_per_day_ml) <= 0
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['alcohol_avg_per_day_ml'],
                message: t('patientForm.validation.required'),
            });
        }
        if (!val.alcohol_drink_type || val.alcohol_drink_type.trim() === '') {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['alcohol_drink_type'],
                message: t('patientForm.validation.required'),
            });
        }
    }
    if (val.alcohol_consumption === 'daily') {
        if (
            !val.alcohol_avg_per_day_ml ||
            isNaN(num(val.alcohol_avg_per_day_ml)) ||
            num(val.alcohol_avg_per_day_ml) <= 0
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['alcohol_avg_per_day_ml'],
                message: t('patientForm.validation.required'),
            });
        }
        if (!val.alcohol_drink_type || val.alcohol_drink_type.trim() === '') {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['alcohol_drink_type'],
                message: t('patientForm.validation.required'),
            });
        }
    }

    // Smoking conditional requirements
    if (val.smoking_habit === 'used_to_quit') {
        if (
            !val.smoking_start_age ||
            isNaN(num(val.smoking_start_age)) ||
            num(val.smoking_start_age) < 0
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['smoking_start_age'],
                message: t('patientForm.validation.required'),
            });
        }
        if (
            !val.smoking_end_age ||
            isNaN(num(val.smoking_end_age)) ||
            num(val.smoking_end_age) <= 0
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['smoking_end_age'],
                message: t('patientForm.validation.required'),
            });
        }
        const sa = num(val.smoking_start_age);
        const ea = num(val.smoking_end_age);
        if (!isNaN(sa) && !isNaN(ea) && ea <= sa) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['smoking_end_age'],
                message: t('patientForm.validation.required'),
            });
        }
        if (
            !val.smoking_cigarettes_per_day ||
            isNaN(num(val.smoking_cigarettes_per_day)) ||
            num(val.smoking_cigarettes_per_day) <= 0
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['smoking_cigarettes_per_day'],
                message: t('patientForm.validation.required'),
            });
        }
    }
    if (val.smoking_habit === 'current') {
        if (
            !val.smoking_start_age ||
            isNaN(num(val.smoking_start_age)) ||
            num(val.smoking_start_age) < 0
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['smoking_start_age'],
                message: t('patientForm.validation.required'),
            });
        }
        if (
            !val.smoking_cigarettes_per_day ||
            isNaN(num(val.smoking_cigarettes_per_day)) ||
            num(val.smoking_cigarettes_per_day) <= 0
        ) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['smoking_cigarettes_per_day'],
                message: t('patientForm.validation.required'),
            });
        }
    }
});

export type PatientFormValues = z.infer<typeof rawSchema>;
const formSchema = toTypedSchema(rawSchema);

const form = useForm<PatientFormValues>({
    validationSchema: formSchema,
    initialValues: {
        full_name: '',
        birthday: '',
        gender: '' as any, // satisfies Select before selection
        occupation: '',
        nationality: '',
        address: '',

        chief_complaint: '',
        medical_history: '',
        past_medical_history: '',
        current_medications: '',
        allergies: '',
        family_medical_history: '',

        alcohol_consumption: '',
        alcohol_per_month_times: '',
        alcohol_per_week_times: '',
        alcohol_per_time_ml: '',
        alcohol_avg_per_day_ml: '',
        alcohol_drink_type: '',

        smoking_habit: '',
        smoking_start_age: '',
        smoking_end_age: '',
        smoking_cigarettes_per_day: '',
        living_situation: '',
        daily_activity_independence: '',
        recent_travel_history: '',

        menstruation_status: '',
        menstrual_cycle: '',
        recent_sexual_activity: null,
    },
});

// Helper computed to estimate years smoked for UI hint
// const currentAgeComputed = computed(() => {
//     const birthday = (form?.values?.birthday as unknown as string) || '';
//     if (!birthday) return undefined as number | undefined;
//     try {
//         const dob = new Date(birthday);
//         const today = new Date();
//         let age = today.getFullYear() - dob.getFullYear();
//         const m = today.getMonth() - dob.getMonth();
//         if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--;
//         return age;
//     } catch {
//         return undefined;
//     }
// });

// const smokingYearsApprox = computed(() => {
//     const v: any = form?.values || {};
//     const start = Number(v.smoking_start_age || NaN);
//     if (isNaN(start)) return undefined as number | undefined;
//     if (v.smoking_habit === 'used_to_quit') {
//         const end = Number(v.smoking_end_age || NaN);
//         if (!isNaN(end) && end > start) return end - start;
//         return undefined;
//     }
//     if (v.smoking_habit === 'current') {
//         const ca = currentAgeComputed.value;
//         if (ca != null && ca > start) return ca - start;
//     }
//     return undefined;
// });

const canSubmit = computed(
    () =>
        (form.meta.value.valid && !loading.value.submit) || loading.value.submit
);

const onSubmit = form.handleSubmit(async (values) => {
    loading.value.submit = true;
    try {
        const toNum = (s?: string | null) => {
            if (s == null) return undefined;
            const n = Number(String(s).trim());
            return isNaN(n) ? undefined : n;
        };
        const calcAge = (birthday: string): number | undefined => {
            if (!birthday) return undefined;
            try {
                const dob = new Date(birthday);
                const today = new Date();
                let age = today.getFullYear() - dob.getFullYear();
                const m = today.getMonth() - dob.getMonth();
                if (m < 0 || (m === 0 && today.getDate() < dob.getDate()))
                    age--;
                return age;
            } catch {
                return undefined;
            }
        };
        const currentAge = calcAge(values.birthday);

        const payload = {
            patient_info: {
                full_name: values.full_name,
                birthday: values.birthday,
                gender: values.gender,
                occupation: values.occupation,
                nationality: values.nationality,
                address: values.address,
            },
            medical_history: {
                chief_complaint: values.chief_complaint,
                medical_history: values.medical_history,
                past_medical_history: values.past_medical_history,
                current_medications: values.current_medications,
                allergies: values.allergies,
                family_medical_history: values.family_medical_history,
            },
            social_information: {
                alcohol_consumption: values.alcohol_consumption,
                alcohol_details:
                    values.alcohol_consumption === 'never'
                        ? undefined
                        : {
                              per_month_times:
                                  values.alcohol_consumption === 'occasionally'
                                      ? toNum(values.alcohol_per_month_times)
                                      : undefined,
                              per_week_times:
                                  values.alcohol_consumption === 'frequently'
                                      ? toNum(values.alcohol_per_week_times)
                                      : undefined,
                              per_time_ml:
                                  values.alcohol_consumption === 'occasionally'
                                      ? toNum(values.alcohol_per_time_ml)
                                      : undefined,
                              avg_per_day_ml:
                                  values.alcohol_consumption === 'frequently' ||
                                  values.alcohol_consumption === 'daily'
                                      ? toNum(values.alcohol_avg_per_day_ml)
                                      : undefined,
                              drink_type:
                                  values.alcohol_consumption !== 'never'
                                      ? values.alcohol_drink_type || undefined
                                      : undefined,
                          },
                smoking_habit: values.smoking_habit,
                smoking_details:
                    values.smoking_habit === 'never'
                        ? undefined
                        : (() => {
                              const start = toNum(values.smoking_start_age);
                              const end =
                                  values.smoking_habit === 'used_to_quit'
                                      ? toNum(values.smoking_end_age)
                                      : undefined;
                              const years = (() => {
                                  if (start == null) return undefined;
                                  if (
                                      values.smoking_habit === 'used_to_quit' &&
                                      end != null
                                  ) {
                                      return end - start;
                                  }
                                  if (
                                      values.smoking_habit === 'current' &&
                                      currentAge != null
                                  ) {
                                      return currentAge - start;
                                  }
                                  return undefined;
                              })();
                              return {
                                  start_age: start,
                                  end_age: end,
                                  cigarettes_per_day: toNum(
                                      values.smoking_cigarettes_per_day
                                  ),
                                  years_smoked: years,
                              };
                          })(),
                living_situation: values.living_situation,
                daily_activity_independence: values.daily_activity_independence,
                recent_travel_history: values.recent_travel_history,
            },
            ...(values.gender === 'Female' && {
                obstetric_gynecological_history: {
                    menstruation_status: values.menstruation_status ?? '',
                    menstrual_cycle: values.menstrual_cycle ?? '',
                    recent_sexual_activity: values.recent_sexual_activity,
                },
            }),
        };

        const response = await chatStore.createNewRecord(userId.value, payload);

        if (user.value) {
            user.value.currentRecordId = response.data.record_id;
            console.log('Set currentRecordId to', user.value.currentRecordId);
        }
        toast.success(t('patientForm.toast.success.title'), {
            description: t('patientForm.toast.success.description'),
        });

        emits('submit', values);
        closeAllDialogs();
        if ((props.mode ?? 'chat') === 'voice') {
            // Open full-screen voice dialog (non-blocking), passing initial AI message to auto-speak
            openDialog({
                component: VoiceCallDialog,
                props: {
                    userId: user.value?.id,
                    recordId: response.data.record_id,
                    initialMessage: response.data.message,
                },
            });
        } else {
            router.push({
                name: 'current-conversation',
            });
        }
        form.resetForm();
    } catch (err) {
        console.error('submitPatientInfo error:', err);
        toast.error(t('patientForm.toast.error.title'), {
            description: t('patientForm.toast.error.description'),
        });
    } finally {
        loading.value.submit = false;
    }
});

/** Helpers for Select binding with vee-validate slot API */
// const bindSelect = (fc: FieldContext<any>) => ({
//     value: fc.value,
//     'onUpdate:modelValue': (v: any) => fc.handleChange(v),
// });
</script>

<template>
    <form
        class="pb-4 max-h-[72vh] overflow-auto max-w-full space-y-6 lg:grid lg:space-y-0 lg:grid-cols-1 lg:gap-x-4 overflow-y-auto overflow-x-clip"
        @submit="onSubmit"
    >
        <!-- Patient Information -->
        <section>
            <h3 class="text-lg font-semibold mb-4">
                {{ $t('patientForm.sections.patientInfo') }}
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <!-- Full Name -->
                <FormField v-slot="{ componentField }" name="full_name">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.fullName') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Input
                                :placeholder="
                                    $t('patientForm.placeholder.fullName')
                                "
                                v-bind="componentField"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <!-- Birthday -->
                <FormField v-slot="{ field }" name="birthday">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.birthday') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Input
                                type="date"
                                v-bind="field"
                                :modelValue="field.value"
                                @update:modelValue="field.onChange"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <!-- Gender -->
                <FormField v-slot="{ field }" name="gender">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.gender') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>

                        <Select
                            :modelValue="field.value"
                            @update:modelValue="field.onChange"
                        >
                            <FormControl>
                                <SelectTrigger>
                                    <SelectValue
                                        :placeholder="
                                            $t('patientForm.options.select')
                                        "
                                    />
                                </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                                <SelectItem value="Male">{{
                                    $t('patientForm.options.male')
                                }}</SelectItem>
                                <SelectItem value="Female">{{
                                    $t('patientForm.options.female')
                                }}</SelectItem>
                                <SelectItem value="Other">{{
                                    $t('patientForm.options.other')
                                }}</SelectItem>
                            </SelectContent>
                        </Select>

                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>
                <!-- Occupation -->
                <FormField v-slot="{ componentField }" name="occupation">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.occupation') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Input
                                :placeholder="
                                    $t('patientForm.placeholder.occupation')
                                "
                                v-bind="componentField"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <!-- Nationality -->
                <FormField v-slot="{ componentField }" name="nationality">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.nationality') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Input
                                :placeholder="
                                    $t('patientForm.placeholder.nationality')
                                "
                                v-bind="componentField"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <!-- Address -->
                <FormField v-slot="{ componentField }" name="address">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.address') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Input
                                :placeholder="
                                    $t('patientForm.placeholder.address')
                                "
                                v-bind="componentField"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>
            </div>

            <hr class="border-t border-dashed border-gray-300 my-6" />
        </section>

        <!-- OB/GYN History -->
        <section v-if="form.values.gender === 'Female'">
            <h3 class="text-lg font-semibold mb-4">
                {{ $t('patientForm.sections.obgynHistory') }}
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <FormField
                    v-slot="{ componentField }"
                    name="menstruation_status"
                >
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.menstruationStatus') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Input
                                :placeholder="
                                    $t(
                                        'patientForm.placeholder.menstruationStatus'
                                    )
                                "
                                v-bind="componentField"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <FormField v-slot="{ componentField }" name="menstrual_cycle">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.menstrualCycle') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Input
                                :placeholder="
                                    $t('patientForm.placeholder.menstrualCycle')
                                "
                                v-bind="componentField"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <FormField v-slot="{ field }" name="recent_sexual_activity">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.recentSexualActivity') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <Select
                            :modelValue="field.value"
                            @update:modelValue="field.onChange"
                        >
                            <FormControl>
                                <SelectTrigger>
                                    <SelectValue
                                        :placeholder="
                                            $t('patientForm.options.select')
                                        "
                                    />
                                </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                                <SelectItem value="true">{{
                                    $t('patientForm.options.yes')
                                }}</SelectItem>
                                <SelectItem value="false">{{
                                    $t('patientForm.options.no')
                                }}</SelectItem>
                            </SelectContent>
                        </Select>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>
            </div>

            <hr class="border-t border-dashed border-gray-300 my-6" />
        </section>

        <!-- Social Information -->
        <section>
            <h3 class="text-lg font-semibold">
                {{ $t('patientForm.sections.socialInfo') }}
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-5 py-5">
                <!-- Alcohol -->
                <FormField v-slot="{ field }" name="alcohol_consumption">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.alcoholConsumption') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <Select
                            :modelValue="field.value"
                            @update:modelValue="field.onChange"
                        >
                            <FormControl>
                                <SelectTrigger>
                                    <SelectValue
                                        :placeholder="
                                            $t('patientForm.options.select')
                                        "
                                    />
                                </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                                <SelectItem value="never">{{
                                    $t('patientForm.options.never')
                                }}</SelectItem>
                                <SelectItem value="occasionally">{{
                                    $t('patientForm.options.occasionally')
                                }}</SelectItem>
                                <SelectItem value="frequently">{{
                                    $t('patientForm.options.frequently')
                                }}</SelectItem>
                                <SelectItem value="daily">{{
                                    $t('patientForm.options.daily')
                                }}</SelectItem>
                            </SelectContent>
                        </Select>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <!-- Alcohol inline details -->
                <div
                    v-if="form.values.alcohol_consumption === 'occasionally'"
                    class="md:col-span-2 -mt-2 text-sm flex flex-wrap items-center gap-2"
                >
                    <span>{{
                        $t('patientForm.inline.alcoholOccasional.prefix')
                    }}</span>
                    <Input
                        class="w-16"
                        type="number"
                        :modelValue="form.values.alcohol_per_month_times"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'alcohol_per_month_times',
                                    String(v ?? '')
                                )
                        "
                    />
                    <span>{{
                        $t('patientForm.inline.alcoholOccasional.times')
                    }}</span>
                    <Input
                        class="w-20"
                        type="number"
                        :modelValue="form.values.alcohol_per_time_ml"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'alcohol_per_time_ml',
                                    String(v ?? '')
                                )
                        "
                    />
                    <span>{{
                        $t('patientForm.inline.alcoholOccasional.ml')
                    }}</span>
                    <Input
                        class="w-40"
                        :modelValue="form.values.alcohol_drink_type"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'alcohol_drink_type',
                                    String(v ?? '')
                                )
                        "
                    />
                </div>

                <div
                    v-if="form.values.alcohol_consumption === 'frequently'"
                    class="md:col-span-2 -mt-2 text-sm flex flex-wrap items-center gap-2"
                >
                    <span>{{
                        $t('patientForm.inline.alcoholFrequent.prefix')
                    }}</span>
                    <Input
                        class="w-16"
                        type="number"
                        :modelValue="form.values.alcohol_per_week_times"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'alcohol_per_week_times',
                                    String(v ?? '')
                                )
                        "
                    />
                    <span>{{
                        $t('patientForm.inline.alcoholFrequent.times')
                    }}</span>
                    <Input
                        class="w-20"
                        type="number"
                        :modelValue="form.values.alcohol_avg_per_day_ml"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'alcohol_avg_per_day_ml',
                                    String(v ?? '')
                                )
                        "
                    />
                    <span>{{
                        $t('patientForm.inline.alcoholFrequent.ml')
                    }}</span>
                    <Input
                        class="w-40"
                        :modelValue="form.values.alcohol_drink_type"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'alcohol_drink_type',
                                    String(v ?? '')
                                )
                        "
                    />
                </div>

                <div
                    v-if="form.values.alcohol_consumption === 'daily'"
                    class="md:col-span-2 -mt-2 text-sm flex flex-wrap items-center gap-2"
                >
                    <span>{{
                        $t('patientForm.inline.alcoholDaily.prefix')
                    }}</span>
                    <Input
                        class="w-20"
                        type="number"
                        :modelValue="form.values.alcohol_avg_per_day_ml"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'alcohol_avg_per_day_ml',
                                    String(v ?? '')
                                )
                        "
                    />
                    <span>{{ $t('patientForm.inline.alcoholDaily.ml') }}</span>
                    <Input
                        class="w-40"
                        :modelValue="form.values.alcohol_drink_type"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'alcohol_drink_type',
                                    String(v ?? '')
                                )
                        "
                    />
                </div>

                <!-- Smoking -->
                <FormField v-slot="{ field }" name="smoking_habit">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.smokingHabit') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <Select
                            :modelValue="field.value"
                            @update:modelValue="field.onChange"
                        >
                            <FormControl>
                                <SelectTrigger>
                                    <SelectValue
                                        :placeholder="
                                            $t('patientForm.options.select')
                                        "
                                    />
                                </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                                <SelectItem value="never">{{
                                    $t('patientForm.options.never')
                                }}</SelectItem>
                                <SelectItem value="used_to_quit">{{
                                    $t('patientForm.options.usedToQuit')
                                }}</SelectItem>
                                <SelectItem value="current">{{
                                    $t('patientForm.options.currentSmoking')
                                }}</SelectItem>
                            </SelectContent>
                        </Select>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <!-- Smoking inline details -->
                <div
                    v-if="form.values.smoking_habit === 'used_to_quit'"
                    class="md:col-span-2 -mt-2 text-sm flex flex-wrap items-center gap-2"
                >
                    <span>{{
                        $t('patientForm.inline.smokingQuit.prefix')
                    }}</span>
                    <Input
                        class="w-16"
                        type="number"
                        :modelValue="form.values.smoking_start_age"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'smoking_start_age',
                                    String(v ?? '')
                                )
                        "
                    />
                    <span>{{ $t('patientForm.inline.smokingQuit.to') }}</span>
                    <Input
                        class="w-16"
                        type="number"
                        :modelValue="form.values.smoking_end_age"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'smoking_end_age',
                                    String(v ?? '')
                                )
                        "
                    />
                    <span
                        >• {{ $t('patientForm.inline.smokingQuit.cigs') }}</span
                    >
                    <Input
                        class="w-16"
                        type="number"
                        :modelValue="form.values.smoking_cigarettes_per_day"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'smoking_cigarettes_per_day',
                                    String(v ?? '')
                                )
                        "
                    />
                    <span>{{
                        $t('patientForm.inline.smokingQuit.cigsUnit')
                    }}</span>
                </div>

                <div
                    v-if="form.values.smoking_habit === 'current'"
                    class="md:col-span-2 -mt-2 text-sm flex flex-wrap items-center gap-2"
                >
                    <span>{{
                        $t('patientForm.inline.smokingCurrent.prefix')
                    }}</span>
                    <Input
                        class="w-16"
                        type="number"
                        :modelValue="form.values.smoking_start_age"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'smoking_start_age',
                                    String(v ?? '')
                                )
                        "
                    />
                    <span>{{
                        $t('patientForm.inline.smokingCurrent.toNow')
                    }}</span>
                    <span
                        >•
                        {{ $t('patientForm.inline.smokingCurrent.cigs') }}</span
                    >
                    <Input
                        class="w-16"
                        type="number"
                        :modelValue="form.values.smoking_cigarettes_per_day"
                        @update:modelValue="
                            (v) =>
                                form.setFieldValue(
                                    'smoking_cigarettes_per_day',
                                    String(v ?? '')
                                )
                        "
                    />
                    <span>{{
                        $t('patientForm.inline.smokingCurrent.cigsUnit')
                    }}</span>
                </div>

                <!-- Living situation -->
                <FormField v-slot="{ field }" name="living_situation">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.livingSituation') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <Select
                            :modelValue="field.value"
                            @update:modelValue="field.onChange"
                        >
                            <FormControl>
                                <SelectTrigger>
                                    <SelectValue
                                        :placeholder="
                                            $t('patientForm.options.select')
                                        "
                                    />
                                </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                                <SelectItem value="alone">{{
                                    $t('patientForm.options.liveAlone')
                                }}</SelectItem>
                                <SelectItem value="family">{{
                                    $t('patientForm.options.liveWithFamily')
                                }}</SelectItem>
                                <SelectItem value="assisted">{{
                                    $t('patientForm.options.assistedLiving')
                                }}</SelectItem>
                                <SelectItem value="other">{{
                                    $t('patientForm.options.otherLiving')
                                }}</SelectItem>
                            </SelectContent>
                        </Select>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <!-- Daily independence -->
                <FormField
                    v-slot="{ field }"
                    name="daily_activity_independence"
                >
                    <FormItem>
                        <FormLabel>
                            {{
                                $t(
                                    'patientForm.fields.dailyActivityIndependence'
                                )
                            }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <Select
                            :modelValue="field.value"
                            @update:modelValue="field.onChange"
                        >
                            <FormControl>
                                <SelectTrigger>
                                    <SelectValue
                                        :placeholder="
                                            $t('patientForm.options.select')
                                        "
                                    />
                                </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                                <SelectItem value="yes">{{
                                    $t('patientForm.options.yes')
                                }}</SelectItem>
                                <SelectItem value="partially">{{
                                    $t('patientForm.options.partially')
                                }}</SelectItem>
                                <SelectItem value="needs_assistance">{{
                                    $t('patientForm.options.needsAssistance')
                                }}</SelectItem>
                            </SelectContent>
                        </Select>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <!-- Travel -->
                <FormField v-slot="{ field }" name="recent_travel_history">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.recentTravelHistory') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <Select
                            :modelValue="field.value"
                            @update:modelValue="field.onChange"
                        >
                            <FormControl>
                                <SelectTrigger>
                                    <SelectValue
                                        :placeholder="
                                            $t('patientForm.options.select')
                                        "
                                    />
                                </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                                <SelectItem value="no">{{
                                    $t('patientForm.options.no')
                                }}</SelectItem>
                                <SelectItem value="14_days">{{
                                    $t('patientForm.options.travel14')
                                }}</SelectItem>
                                <SelectItem value="1_month">{{
                                    $t('patientForm.options.travelMonth')
                                }}</SelectItem>
                            </SelectContent>
                        </Select>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>
            </div>

            <hr class="border-t border-dashed border-gray-300 my-6" />
        </section>

        <!-- Medical History -->
        <section>
            <h3 class="text-lg font-semibold mb-4">
                {{ $t('patientForm.sections.medicalHistory') }}
            </h3>

            <div class="flex flex-col gap-6">
                <!-- Past Medical History -->
                <FormField
                    v-slot="{ componentField }"
                    name="past_medical_history"
                >
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.pastMedicalHistory') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Textarea
                                rows="3"
                                class="min-h-[100px]"
                                :placeholder="
                                    $t(
                                        'patientForm.placeholder.pastMedicalHistory'
                                    )
                                "
                                v-bind="componentField"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <!-- Current Medications -->
                <FormField
                    v-slot="{ componentField }"
                    name="current_medications"
                >
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.currentMedications') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Textarea
                                rows="3"
                                class="min-h-[100px]"
                                :placeholder="
                                    $t('patientForm.placeholder.medication')
                                "
                                v-bind="componentField"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <!-- Allergies -->
                <FormField v-slot="{ componentField }" name="allergies">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.allergies') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Textarea
                                rows="3"
                                class="min-h-[100px]"
                                :placeholder="
                                    $t('patientForm.placeholder.allergy')
                                "
                                v-bind="componentField"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>

                <!-- Family Medical History -->
                <FormField
                    v-slot="{ componentField }"
                    name="family_medical_history"
                >
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.familyMedicalHistory') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Textarea
                                rows="3"
                                class="min-h-[100px]"
                                :placeholder="
                                    $t(
                                        'patientForm.placeholder.familyMedicalHistory'
                                    )
                                "
                                v-bind="componentField"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>
            </div>

            <hr class="border-t border-dashed border-gray-300 my-6" />
        </section>

        <!-- Reason for Visit -->
        <section>
            <h3 class="text-lg font-semibold mb-4">
                {{ $t('patientForm.sections.reasonForVisit') }}
            </h3>

            <div class="grid grid-cols-1 gap-4 pb-5">
                <!-- Chief Complaint -->
                <FormField v-slot="{ componentField }" name="chief_complaint">
                    <FormItem>
                        <FormLabel>
                            {{ $t('patientForm.fields.chiefComplaint') }}
                            <span class="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                            <Textarea
                                rows="3"
                                class="min-h-[100px]"
                                :placeholder="
                                    $t('patientForm.placeholder.chiefComplaint')
                                "
                                v-bind="componentField"
                            />
                        </FormControl>
                        <div class="lg:min-h-6">
                            <FormMessage />
                        </div>
                    </FormItem>
                </FormField>
            </div>

            <!-- Symptom Progression -->
            <FormField v-slot="{ componentField }" name="medical_history">
                <FormItem>
                    <FormLabel>
                        {{ $t('patientForm.fields.medicalHistory') }}
                        <span class="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                        <Textarea
                            rows="3"
                            class="min-h-[100px]"
                            :placeholder="
                                $t('patientForm.placeholder.medicalHistory')
                            "
                            v-bind="componentField"
                        />
                    </FormControl>
                    <div class="lg:min-h-6">
                        <FormMessage />
                    </div>
                </FormItem>
            </FormField>
        </section>

        <!-- Submit -->
        <div class="flex justify-center">
            <Button
                :disabled="!canSubmit"
                type="submit"
                class="w-full md:w-auto"
            >
                <Loader2
                    v-if="loading.submit"
                    class="animate-spin w-4 h-4 mr-2"
                />
                <Check v-else class="w-4 h-4 mr-2" />
                {{
                    loading.submit
                        ? $t('patientForm.submit.submitting')
                        : $t('patientForm.submit.default')
                }}
            </Button>
        </div>
    </form>
</template>
