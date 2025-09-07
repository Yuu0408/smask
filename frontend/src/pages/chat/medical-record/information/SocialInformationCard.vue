<script setup lang="ts">
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
    CardFooter,
} from '@/components/ui/card';
import Button from '@/components/ui/button/Button.vue';
import Label from '@/components/ui/label/Label.vue';
</script>

<template>
    <Card>
        <CardHeader>
            <CardTitle>
                Social Information
                <CardDescription>
                    Please fill in the social information
                </CardDescription>
            </CardTitle>
        </CardHeader>
        <CardContent>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-5 py-5">
                    <div>
                        <Label class="py-1" for="alcohol_consumption">{{
                            $t('patientForm.fields.alcoholConsumption')
                        }}</Label>
                        <select
                            id="alcohol_consumption"
                            class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                        >
                            <option value="" disabled>
                                {{ $t('patientForm.options.select') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.never') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.occasionally') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.frequently') }}
                            </option>
                        </select>
                    </div>

                    <div>
                        <Label class="py-1" for="smoking_habit">{{
                            $t('patientForm.fields.smokingHabit')
                        }}</Label>
                        <select
                            id="smoking_habit"
                            class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                        >
                            <option value="" disabled>
                                {{ $t('patientForm.options.select') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.never') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.usedToQuit') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.occasionally') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.daily') }}
                            </option>
                        </select>
                    </div>

                    <div>
                        <Label class="py-1" for="living_situation">{{
                            $t('patientForm.fields.livingSituation')
                        }}</Label>
                        <select
                            id="living_situation"
                            class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                        >
                            <option value="" disabled>
                                {{ $t('patientForm.options.select') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.liveAlone') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.liveWithFamily') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.assistedLiving') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.otherLiving') }}
                            </option>
                        </select>
                    </div>

                    <div>
                        <Label class="py-1" for="daily_activity_independence">{{
                            $t('patientForm.fields.dailyActivityIndependence')
                        }}</Label>
                        <select
                            id="daily_activity_independence"
                            class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                        >
                            <option value="" disabled>
                                {{ $t('patientForm.options.select') }}
                            </option>
                            <option>{{ $t('patientForm.options.yes') }}</option>
                            <option>
                                {{ $t('patientForm.options.partially') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.needsAssistance') }}
                            </option>
                        </select>
                    </div>

                    <div>
                        <Label class="py-1" for="recent_travel_history">{{
                            $t('patientForm.fields.recentTravelHistory')
                        }}</Label>
                        <select
                            id="recent_travel_history"
                            class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                        >
                            <option value="" disabled>
                                {{ $t('patientForm.options.select') }}
                            </option>
                            <option>{{ $t('patientForm.options.no') }}</option>
                            <option>
                                {{ $t('patientForm.options.travel14') }}
                            </option>
                            <option>
                                {{ $t('patientForm.options.travelMonth') }}
                            </option>
                        </select>
                    </div>
                </div>
            </div>
        </CardContent>
        <CardFooter class="flex justify-end">
            <div class="grid grid-cols-2 gap-1">
                <Button variant="outline">Previous</Button>
                <Button>Next</Button>
            </div>
        </CardFooter>
    </Card>
</template>
