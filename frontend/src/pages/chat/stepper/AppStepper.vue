<script setup lang="ts">
import { BookUser, Check, CreditCard, Truck } from 'lucide-vue-next';

import {
    Stepper,
    StepperDescription,
    StepperIndicator,
    StepperItem,
    StepperSeparator,
    StepperTitle,
    StepperTrigger,
} from '@/components/ui/stepper';

const steps = [
    {
        step: 1,
        title: 'Bước 1',
        description: 'Khai báo thông tin cơ bản',
        icon: BookUser,
    },
    {
        step: 2,
        title: 'Bước 2',
        description: 'Khai báo thông tin xã hội',
        icon: Truck,
    },
    {
        step: 3,
        title: 'Bước 3',
        description: 'Khai báo thông tin bệnh lý',
        icon: CreditCard,
    },
    {
        step: 4,
        title: 'Bắt đầu',
        description: 'Bắt đầu chẩn đoán',
        icon: Check,
    },
];
</script>

<template>
    <Stepper class="pl-20 mb-8 w-full">
        <StepperItem
            v-for="item in steps"
            :key="item.step"
            class="basis-1/4"
            :step="item.step"
        >
            <StepperTrigger>
                <StepperIndicator>
                    <component :is="item.icon" class="w-4 h-4" />
                </StepperIndicator>
                <div class="flex flex-col">
                    <StepperTitle>
                        {{ item.title }}
                    </StepperTitle>
                    <StepperDescription>
                        {{ item.description }}
                    </StepperDescription>
                </div>
            </StepperTrigger>
            <StepperSeparator
                v-if="item.step !== steps[steps.length - 1].step"
                class="w-full h-px"
            />
        </StepperItem>
    </Stepper>
</template>
