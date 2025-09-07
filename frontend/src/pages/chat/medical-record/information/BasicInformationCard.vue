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
import Input from '@/components/ui/input/Input.vue';
import Label from '@/components/ui/label/Label.vue';
</script>

<template>
    <Card>
        <CardHeader>
            <CardTitle>
                Basic Information
                <CardDescription>
                    Please fill in the basic information
                </CardDescription>
            </CardTitle>
        </CardHeader>
        <CardContent>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                    <Label class="py-1" for="full_name">{{
                        $t('patientForm.fields.fullName')
                    }}</Label>
                    <Input
                        id="full_name"
                        :placeholder="$t('patientForm.placeholder.fullName')"
                        required
                    />
                </div>

                <div>
                    <Label class="py-1" for="birthday">{{
                        $t('patientForm.fields.birthday')
                    }}</Label>
                    <input
                        type="date"
                        id="birthday"
                        class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                        required
                    />
                </div>

                <div>
                    <Label class="py-1" for="gender">{{
                        $t('patientForm.fields.gender')
                    }}</Label>
                    <select
                        id="gender"
                        required
                        class="w-full border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm shadow-sm"
                    >
                        <option value="" disabled>
                            {{ $t('patientForm.options.select') }}
                        </option>
                        <option value="Male">
                            {{ $t('patientForm.options.male') }}
                        </option>
                        <option value="Female">
                            {{ $t('patientForm.options.female') }}
                        </option>
                        <option value="Other">
                            {{ $t('patientForm.options.other') }}
                        </option>
                    </select>
                </div>

                <div>
                    <Label class="py-1" for="occupation">{{
                        $t('patientForm.fields.occupation')
                    }}</Label>
                    <Input
                        id="occupation"
                        :placeholder="$t('patientForm.placeholder.occupation')"
                        required
                    />
                </div>

                <div>
                    <Label class="py-1" for="nationality">{{
                        $t('patientForm.fields.nationality')
                    }}</Label>
                    <Input
                        id="nationality"
                        :placeholder="$t('patientForm.placeholder.nationality')"
                        required
                    />
                </div>
                <div>
                    <Label class="py-1" for="address">{{
                        $t('patientForm.fields.address')
                    }}</Label>
                    <Input
                        id="address"
                        :placeholder="$t('patientForm.placeholder.address')"
                        required
                    />
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
