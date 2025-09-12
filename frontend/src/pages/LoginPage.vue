<script setup lang="ts">
import { onBeforeMount, ref } from 'vue';
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
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

const auth = useAuthStore();
const { t } = useI18n();
const router = useRouter();

const username = ref('');
const password = ref('');
const loading = ref(false);
const registerEnabled = ref(false);
const error = ref<string | null>(null);

async function handleLoginSubmit() {
    error.value = null;
    loading.value = true;
    try {
        await auth.login(username.value, password.value);
        // after successful login, route to home (example)
        router.push({ name: 'home' });
    } catch (e: any) {
        error.value = e?.response?.data?.detail || 'Login failed';
    } finally {
        loading.value = false;
    }
}

async function handleRegisterSubmit() {
    error.value = null;
    loading.value = true;
    try {
        await auth.register(username.value, password.value);
        router.push({ name: 'home' });
    } catch (e: any) {
        error.value = e?.response?.data?.detail || 'Registration failed';
    } finally {
        loading.value = false;
    }
}

function enableRegister() {
    registerEnabled.value = true;
}

onBeforeMount(() => {
    registerEnabled.value = false;
    console.log(`registerEnabled value: `, registerEnabled.value);
});
</script>

<template>
    <div class="flex min-h-screen items-center justify-center bg-gray-50">
        <Card class="w-full max-w-md" v-if="!registerEnabled">
            <CardHeader>
                <CardTitle class="text-center">{{
                    t('page.login.title')
                }}</CardTitle>
            </CardHeader>

            <form @submit.prevent="handleLoginSubmit">
                <CardContent class="space-y-4">
                    <div class="space-y-2">
                        <Label for="username">{{
                            t('page.login.label.username')
                        }}</Label>
                        <Input
                            id="username"
                            v-model="username"
                            type="username"
                            required
                        />
                    </div>
                    <div class="space-y-2">
                        <Label for="password">{{
                            t('page.login.label.password')
                        }}</Label>
                        <Input
                            id="password"
                            v-model="password"
                            type="password"
                            required
                        />
                    </div>
                    <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
                </CardContent>

                <CardFooter class="grid grid-row-2 gap-2 mt-4">
                    <Button type="submit" :disabled="loading" class="w-full">
                        <span v-if="!loading">{{
                            t('page.login.button.login')
                        }}</span>
                        <span v-else>{{ t('page.login.button.loading') }}</span>
                    </Button>
                    <Button variant="secondary" @click="enableRegister">
                        <span>{{ t('page.login.button.register') }}</span>
                    </Button>
                </CardFooter>
            </form>
        </Card>
        <Card class="w-full max-w-md" v-else>
            <CardHeader>
                <CardTitle class="text-center">{{
                    t('page.login.title')
                }}</CardTitle>
            </CardHeader>

            <form @submit.prevent="handleRegisterSubmit">
                <CardContent class="space-y-4">
                    <div class="space-y-2">
                        <Label for="username">{{
                            t('page.login.label.username')
                        }}</Label>
                        <Input
                            id="username"
                            v-model="username"
                            type="username"
                            required
                        />
                    </div>
                    <div class="space-y-2">
                        <Label for="password">{{
                            t('page.login.label.password')
                        }}</Label>
                        <Input
                            id="password"
                            v-model="password"
                            type="password"
                            required
                        />
                    </div>
                    <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
                </CardContent>

                <CardFooter class="grid grid-row-2 gap-2 mt-4">
                    <Button type="submit" :disabled="loading" class="w-full">
                        <span v-if="!loading">{{
                            t('page.login.button.register')
                        }}</span>
                        <span v-else>{{ t('page.login.button.loading') }}</span>
                    </Button>
                </CardFooter>
            </form>
        </Card>
    </div>
</template>
