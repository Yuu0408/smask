<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

// shadcn-vue components
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    CardFooter,
} from '@/components/ui/card';

const auth = useAuthStore();

const email = ref('');
const password = ref('');
const loading = ref(false);
const error = ref<string | null>(null);

async function handleSubmit() {
    error.value = null;
    loading.value = true;
    try {
        await auth.login(email.value, password.value);
        // after successful login, route to home (example)
        // router.push({ name: 'home' })
    } catch (e: any) {
        error.value = e?.response?.data?.detail || 'Login failed';
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <div class="flex min-h-screen items-center justify-center bg-gray-50">
        <Card class="w-full max-w-md">
            <CardHeader>
                <CardTitle class="text-center">Login</CardTitle>
            </CardHeader>

            <form @submit.prevent="handleSubmit">
                <CardContent class="space-y-4">
                    <div class="space-y-2">
                        <Label for="email">Email</Label>
                        <Input
                            id="email"
                            v-model="email"
                            type="email"
                            required
                        />
                    </div>
                    <div class="space-y-2">
                        <Label for="password">Password</Label>
                        <Input
                            id="password"
                            v-model="password"
                            type="password"
                            required
                        />
                    </div>
                    <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
                </CardContent>

                <CardFooter class="flex justify-end">
                    <Button type="submit" :disabled="loading" class="w-full">
                        <span v-if="!loading">Sign In</span>
                        <span v-else>Loading...</span>
                    </Button>
                </CardFooter>
            </form>
        </Card>
    </div>
</template>
