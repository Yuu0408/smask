<template>
  <Dialog :open="open" @update:open="handleCloseAttempt">
    <DialogContent class="sm:max-w-4xl w-full rounded-2xl">
      <DialogHeader>
        <DialogTitle>{{ $t("patientForm.title") }}</DialogTitle>
        <DialogDescription>
          {{ $t("patientForm.description") }}
        </DialogDescription>
        <div class="flex justify-end mt-4 mr-4">
          <label class="mr-2 pt-1 font-medium text-sm">{{
            $t("patientForm.language")
          }}</label>
          <select
            v-model="selectedLanguage"
            class="border border-input rounded-md text-sm px-2 py-1"
          >
            <option value="en">English</option>
            <option value="vi">Tiếng Việt</option>
          </select>
        </div>
      </DialogHeader>

      <form
        @submit.prevent="submitForm"
        class="max-h-[75vh] overflow-y-auto px-1 pt-4 space-y-8"
      >
        <!-- Patient Information -->
        <section>
          <h3 class="text-lg font-semibold mb-4">
            {{ $t("patientForm.sections.patientInfo") }}
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <Label class="py-1" for="full_name">{{
                $t("patientForm.fields.fullName")
              }}</Label>
              <Input
                id="full_name"
                v-model="form.full_name"
                :placeholder="$t('patientForm.placeholder.fullName')"
                required
              />
            </div>

            <div>
              <Label class="py-1" for="birthday">{{
                $t("patientForm.fields.birthday")
              }}</Label>
              <input
                type="date"
                id="birthday"
                v-model="form.birthday"
                class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                required
              />
            </div>

            <div>
              <Label class="py-1" for="gender">{{
                $t("patientForm.fields.gender")
              }}</Label>
              <select
                id="gender"
                v-model="form.gender"
                required
                class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
              >
                <option value="" disabled>
                  {{ $t("patientForm.options.select") }}
                </option>
                <option value="Male">
                  {{ $t("patientForm.options.male") }}
                </option>
                <option value="Female">
                  {{ $t("patientForm.options.female") }}
                </option>
                <option value="Other">
                  {{ $t("patientForm.options.other") }}
                </option>
              </select>
            </div>

            <div>
              <Label class="py-1" for="occupation">{{
                $t("patientForm.fields.occupation")
              }}</Label>
              <Input
                id="occupation"
                v-model="form.occupation"
                :placeholder="$t('patientForm.placeholder.occupation')"
                required
              />
            </div>

            <div>
              <Label class="py-1" for="nationality">{{
                $t("patientForm.fields.nationality")
              }}</Label>
              <Input
                id="nationality"
                v-model="form.nationality"
                :placeholder="$t('patientForm.placeholder.nationality')"
                required
              />
            </div>
            <div>
              <Label class="py-1" for="address">{{
                $t("patientForm.fields.address")
              }}</Label>
              <Input
                id="address"
                v-model="form.address"
                :placeholder="$t('patientForm.placeholder.address')"
                required
              />
            </div>
          </div>
        </section>

        <!-- OB/GYN History -->
        <section v-if="form.gender === 'Female'">
          <h3 class="text-lg font-semibold mb-4">
            {{ $t("patientForm.sections.obgynHistory") }}
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <Label class="py-1" for="menstruation_status">{{
                $t("patientForm.fields.menstruationStatus")
              }}</Label>
              <Input
                id="menstruation_status"
                v-model="form.menstruation_status"
                :placeholder="$t('patientForm.placeholder.menstruationStatus')"
              />
            </div>
            <div>
              <Label class="py-1" for="menstrual_cycle">{{
                $t("patientForm.fields.menstrualCycle")
              }}</Label>
              <Input
                id="menstrual_cycle"
                v-model="form.menstrual_cycle"
                :placeholder="$t('patientForm.placeholder.menstrualCycle')"
              />
            </div>
            <div>
              <Label class="py-1" for="recent_sexual_activity">{{
                $t("patientForm.fields.recentSexualActivity")
              }}</Label>
              <select
                id="recent_sexual_activity"
                v-model="form.recent_sexual_activity"
                class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
              >
                <option :value="null">
                  {{ $t("patientForm.options.select") }}
                </option>
                <option :value="true">
                  {{ $t("patientForm.options.yes") }}
                </option>
                <option :value="false">
                  {{ $t("patientForm.options.no") }}
                </option>
              </select>
            </div>
          </div>
        </section>
        <hr class="border-t border-gray-300 my-6" />

        <!-- Social Information -->
        <section>
          <h3 class="text-lg font-semibold">
            {{ $t("patientForm.sections.socialInfo") }}
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5 py-5">
            <div>
              <Label class="py-1" for="alcohol_consumption">{{
                $t("patientForm.fields.alcoholConsumption")
              }}</Label>
              <select
                v-model="form.alcohol_consumption"
                id="alcohol_consumption"
                class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
              >
                <option value="" disabled>
                  {{ $t("patientForm.options.select") }}
                </option>
                <option>{{ $t("patientForm.options.never") }}</option>
                <option>{{ $t("patientForm.options.occasionally") }}</option>
                <option>{{ $t("patientForm.options.frequently") }}</option>
              </select>
            </div>

            <div>
              <Label class="py-1" for="smoking_habit">{{
                $t("patientForm.fields.smokingHabit")
              }}</Label>
              <select
                v-model="form.smoking_habit"
                id="smoking_habit"
                class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
              >
                <option value="" disabled>
                  {{ $t("patientForm.options.select") }}
                </option>
                <option>{{ $t("patientForm.options.never") }}</option>
                <option>{{ $t("patientForm.options.usedToQuit") }}</option>
                <option>{{ $t("patientForm.options.occasionally") }}</option>
                <option>{{ $t("patientForm.options.daily") }}</option>
              </select>
            </div>

            <div>
              <Label class="py-1" for="living_situation">{{
                $t("patientForm.fields.livingSituation")
              }}</Label>
              <select
                v-model="form.living_situation"
                id="living_situation"
                class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
              >
                <option value="" disabled>
                  {{ $t("patientForm.options.select") }}
                </option>
                <option>{{ $t("patientForm.options.liveAlone") }}</option>
                <option>{{ $t("patientForm.options.liveWithFamily") }}</option>
                <option>{{ $t("patientForm.options.assistedLiving") }}</option>
                <option>{{ $t("patientForm.options.otherLiving") }}</option>
              </select>
            </div>

            <div>
              <Label class="py-1" for="daily_activity_independence">{{
                $t("patientForm.fields.dailyActivityIndependence")
              }}</Label>
              <select
                v-model="form.daily_activity_independence"
                id="daily_activity_independence"
                class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
              >
                <option value="" disabled>
                  {{ $t("patientForm.options.select") }}
                </option>
                <option>{{ $t("patientForm.options.yes") }}</option>
                <option>{{ $t("patientForm.options.partially") }}</option>
                <option>{{ $t("patientForm.options.needsAssistance") }}</option>
              </select>
            </div>

            <div>
              <Label class="py-1" for="recent_travel_history">{{
                $t("patientForm.fields.recentTravelHistory")
              }}</Label>
              <select
                v-model="form.recent_travel_history"
                id="recent_travel_history"
                class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
              >
                <option value="" disabled>
                  {{ $t("patientForm.options.select") }}
                </option>
                <option>{{ $t("patientForm.options.no") }}</option>
                <option>{{ $t("patientForm.options.travel14") }}</option>
                <option>{{ $t("patientForm.options.travelMonth") }}</option>
              </select>
            </div>
          </div>
        </section>
        <!-- Medical History -->
        <section>
          <h3 class="text-lg font-semibold mb-4">
            {{ $t("patientForm.sections.medicalHistory") }}
          </h3>
          <div class="flex flex-col gap-6">
            <!-- Past Medical History -->
            <div>
              <Label class="py-1" for="has_past_medical_history">{{
                $t("patientForm.fields.pastMedicalHistory")
              }}</Label>
              <div class="flex flex-col md:flex-row items-center gap-4">
                <select
                  id="has_past_medical_history"
                  v-model="form.has_past_medical_history"
                  class="md:w-1/3 w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                >
                  <option value="">
                    {{ $t("patientForm.options.select") }}
                  </option>
                  <option value="yes">
                    {{ $t("patientForm.options.yes") }}
                  </option>
                  <option value="no">{{ $t("patientForm.options.no") }}</option>
                </select>
                <Input
                  v-if="form.has_past_medical_history === 'yes'"
                  v-model="form.past_medical_history"
                  :placeholder="
                    $t('patientForm.placeholder.pastMedicalHistory')
                  "
                  class="flex-1 w-full"
                />
              </div>
            </div>

            <!-- Current Medications -->
            <div>
              <Label class="py-1" for="has_current_medications">{{
                $t("patientForm.fields.currentMedications")
              }}</Label>
              <div class="flex flex-col md:flex-row items-center gap-4">
                <select
                  id="has_current_medications"
                  v-model="form.has_current_medications"
                  class="md:w-1/3 w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                >
                  <option value="">
                    {{ $t("patientForm.options.select") }}
                  </option>
                  <option value="yes">
                    {{ $t("patientForm.options.yes") }}
                  </option>
                  <option value="no">{{ $t("patientForm.options.no") }}</option>
                </select>
                <Input
                  v-if="form.has_current_medications === 'yes'"
                  v-model="form.current_medications"
                  :placeholder="$t('patientForm.placeholder.medication')"
                  class="flex-1 w-full"
                />
              </div>
            </div>

            <!-- Allergies -->
            <div>
              <Label class="py-1" for="has_allergies">{{
                $t("patientForm.fields.allergies")
              }}</Label>
              <div class="flex flex-col md:flex-row items-center gap-4">
                <select
                  id="has_allergies"
                  v-model="form.has_allergies"
                  class="md:w-1/3 w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                >
                  <option value="">
                    {{ $t("patientForm.options.select") }}
                  </option>
                  <option value="yes">
                    {{ $t("patientForm.options.yes") }}
                  </option>
                  <option value="no">{{ $t("patientForm.options.no") }}</option>
                </select>
                <Input
                  v-if="form.has_allergies === 'yes'"
                  v-model="form.allergies"
                  :placeholder="$t('patientForm.placeholder.allergy')"
                  class="flex-1 w-full"
                />
              </div>
            </div>

            <!-- Family Medical History -->
            <div>
              <Label class="py-1" for="has_family_medical_history">{{
                $t("patientForm.fields.familyMedicalHistory")
              }}</Label>
              <div class="flex flex-col md:flex-row items-center gap-4">
                <select
                  id="has_family_medical_history"
                  v-model="form.has_family_medical_history"
                  class="md:w-1/3 w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                >
                  <option value="">
                    {{ $t("patientForm.options.select") }}
                  </option>
                  <option value="yes">
                    {{ $t("patientForm.options.yes") }}
                  </option>
                  <option value="no">{{ $t("patientForm.options.no") }}</option>
                </select>
                <Input
                  v-if="form.has_family_medical_history === 'yes'"
                  v-model="form.family_medical_history"
                  :placeholder="
                    $t('patientForm.placeholder.familyMedicalHistory')
                  "
                  class="flex-1 w-full"
                />
              </div>
            </div>
          </div>
        </section>

        <!-- Reason for Visit -->
        <section>
          <div class="grid grid-cols-1 gap-4 pb-5">
            <div>
              <Label class="py-1" for="chief_complaint">{{
                $t("patientForm.fields.chiefComplaint")
              }}</Label>
              <textarea
                id="chief_complaint"
                v-model="form.chief_complaint"
                :placeholder="$t('patientForm.placeholder.chiefComplaint')"
                rows="3"
                class="w-full resize-x border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-ring"
              ></textarea>
            </div>
          </div>
          <!-- Symptom Progression -->
          <div class="col-span-1 md:col-span-2">
            <Label class="py-1" for="medical_history">{{
              $t("patientForm.fields.medicalHistory")
            }}</Label>
            <textarea
              id="medical_history"
              v-model="form.medical_history"
              :placeholder="$t('patientForm.placeholder.medicalHistory')"
              rows="3"
              class="w-full border rounded-md px-3 py-2 text-sm shadow-sm"
            ></textarea>
          </div>
        </section>

        <!-- Warning + Submit -->
        <p v-if="showWarning" class="text-sm text-red-500 mt-2">
          {{ $t("patientForm.warning") }}
        </p>

        <DialogFooter class="pt-4">
          <Button
            type="submit"
            class="w-full"
            :disabled="!isFormValid() || submitting"
          >
            {{
              submitting
                ? $t("patientForm.submit.submitting")
                : $t("patientForm.submit.default")
            }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from "vue";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { submitPatientInfo } from "@/api/patientApi";
import { watch } from "vue";
import { useI18n } from "vue-i18n";

const { t, locale } = useI18n();

const selectedLanguage = ref(locale.value);

watch(selectedLanguage, (newLang) => {
  locale.value = newLang;
});

const emit = defineEmits(["submitted", "failed"]);

const submitting = ref(false);
const submitted = ref(false);
const open = ref(true);
const showWarning = ref(false);

const form = ref({
  full_name: "",
  birthday: "",
  gender: "",
  occupation: "",
  nationality: "",
  address: "",
  chief_complaint: "",
  medical_history: "",
  past_medical_history: "",
  current_medications: "",
  allergies: "",
  family_medical_history: "",

  alcohol_consumption: "",
  smoking_habit: "",
  living_situation: "",
  daily_activity_independence: "",
  recent_travel_history: "",

  menstruation_status: "",
  menstrual_cycle: "",
  recent_sexual_activity: null,

  has_past_medical_history: "",
  has_current_medications: "",
  has_allergies: "",
  has_family_medical_history: "",
});

watch(
  () => form.value.has_past_medical_history,
  (newVal) => {
    if (newVal === "no") {
      form.value.past_medical_history = t("patientForm.options.no");
    }
  }
);

watch(
  () => form.value.has_current_medications,
  (newVal) => {
    if (newVal === "no") {
      form.value.current_medications = t("patientForm.options.no");
    }
  }
);

watch(
  () => form.value.has_allergies,
  (newVal) => {
    if (newVal === "no") {
      form.value.allergies = t("patientForm.options.no");
    }
  }
);

watch(
  () => form.value.has_family_medical_history,
  (newVal) => {
    if (newVal === "no") {
      form.value.family_medical_history = t("patientForm.options.no");
    }
  }
);

function isFormValid() {
  const requiredFields = [
    "full_name",
    "birthday",
    "gender",
    "occupation",
    "nationality",
    "address",
    "chief_complaint",
    "alcohol_consumption",
    "smoking_habit",
    "living_situation",
    "daily_activity_independence",
    "recent_travel_history",
    "past_medical_history",
    "current_medications",
    "allergies",
    "family_medical_history",
    "medical_history",
  ];

  // Include OB/GYN fields if gender is Female
  if (form.value.gender === "Female") {
    requiredFields.push(
      "menstruation_status",
      "menstrual_cycle",
      "recent_sexual_activity"
    );
  }

  return requiredFields.every((field) => {
    const value = form.value[field as keyof typeof form.value];
    return value !== "" && value !== null && value !== undefined;
  });
}

function handleCloseAttempt(value: boolean) {
  if (!value && !isFormValid() && !submitted.value) {
    showWarning.value = true;
    open.value = true;
  } else {
    open.value = value;
  }
}

async function submitForm() {
  if (submitting.value || submitted.value) return;
  submitting.value = true;

  try {
    const payload = {
      patient_info: {
        full_name: form.value.full_name,
        birthday: form.value.birthday,
        gender: form.value.gender,
        occupation: form.value.occupation,
        nationality: form.value.nationality,
        address: form.value.address,
      },
      medical_history: {
        chief_complaint: form.value.chief_complaint,
        medical_history: form.value.medical_history,
        past_medical_history: form.value.past_medical_history,
        current_medications: form.value.current_medications,
        allergies: form.value.allergies,
        family_medical_history: form.value.family_medical_history,
      },
      social_information: {
        alcohol_consumption: form.value.alcohol_consumption,
        smoking_habit: form.value.smoking_habit,
        living_situation: form.value.living_situation,
        daily_activity_independence: form.value.daily_activity_independence,
        recent_travel_history: form.value.recent_travel_history,
      },
      ...(form.value.gender === "Female" && {
        obstetric_gynecological_history: {
          menstruation_status: form.value.menstruation_status,
          menstrual_cycle: form.value.menstrual_cycle,
          recent_sexual_activity: form.value.recent_sexual_activity,
        },
      }),
    };

    await submitPatientInfo(payload);
    submitted.value = true;
    emit("submitted", form.value);
    open.value = false;
  } catch (error) {
    emit("failed", error);
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 9999px;
}
::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 9999px;
  border: 2px solid transparent;
  background-clip: content-box;
}
</style>
