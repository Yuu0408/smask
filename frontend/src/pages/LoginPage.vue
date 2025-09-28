<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useI18n } from 'vue-i18n';
import { useRouter, useRoute } from 'vue-router';

// shadcn-vue components
import { Button } from '@/components/ui/button';
import {
    Select,
    SelectTrigger,
    SelectContent,
    SelectItem,
    SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    CardFooter,
} from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

type Role = 'patient' | 'doctor';
type Mode = 'login' | 'register';

const auth = useAuthStore();
const { t, locale } = useI18n();
const router = useRouter();
const route = useRoute();

// UI state
const role = ref<Role>('patient');
const mode = ref<Mode>('login');

// form state
const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const error = ref<string | null>(null);
const doctorAddress = ref('');
const doctorFacility = ref('');

// derived
const formTitle = computed(() =>
    mode.value === 'login'
        ? (t('page.login.form.login_title') as string) || 'Sign in to Medee'
        : (t('page.login.form.register_title') as string) ||
          'Create your Medee account'
);

function resetError() {
    error.value = null;
}

function setLocale(l: 'en' | 'vi') {
    locale.value = l;
    if (typeof window !== 'undefined') {
        window.localStorage.setItem('locale', l);
    }
}

async function handleSubmit() {
    error.value = null;

    if (mode.value === 'register' && password.value !== confirmPassword.value) {
        error.value =
            t('page.login.error.password_mismatch') || 'Passwords do not match';
        return;
    }

    loading.value = true;
    try {
        if (mode.value === 'login') {
            const payload = {
                username: username.value,
                password: password.value,
            };
            await auth.login(payload);
        } else {
            const metadata: import('@/types/auth').UserMetadata | undefined =
                role.value === 'doctor'
                    ? {
                          address: doctorAddress.value,
                          facility: doctorFacility.value,
                      }
                    : undefined;
            if (
                role.value === 'doctor' &&
                (!doctorAddress.value || !doctorFacility.value)
            ) {
                error.value = t(
                    'page.login.error.address_hospital_required'
                ) as string;
                loading.value = false;
                return;
            }
            const payload: import('@/types/auth').registerRequest = {
                username: username.value,
                password: password.value,
                role: role.value,
                metadata,
            };
            await auth.register(payload);
        }
        await auth.getMe();
        const redirect = (route.query.redirect as string) || undefined;
        if (redirect) {
            router.replace(redirect);
        } else {
            if (auth.user?.role === 'doctor') {
                router.push({ name: 'contact.patients' });
            } else {
                router.push({ name: 'home_page' });
            }
        }
    } catch (e: any) {
        error.value =
            e?.response?.data?.detail ||
            (mode.value === 'login'
                ? (t('page.login.error.login_failed') as string) ||
                  'Login failed'
                : (t('page.login.error.register_failed') as string) ||
                  'Registration failed');
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <div
        class="min-h-screen bg-gradient-to-br from-sky-50 via-white to-indigo-50"
    >
        <!-- Top bar -->
        <div
            class="mx-auto max-w-6xl px-4 py-6 flex items-center justify-between"
        >
            <div class="flex items-center gap-2">
                <span class="text-lg font-semibold tracking-tight text-sky-800"
                    >Medee</span
                >
            </div>
            <div class="flex items-center gap-1">
                <Button
                    size="sm"
                    variant="ghost"
                    :class="{ 'bg-sky-100 text-sky-700': locale === 'en' }"
                    @click="setLocale('en')"
                    >EN</Button
                >
                <Button
                    size="sm"
                    variant="ghost"
                    :class="{ 'bg-sky-100 text-sky-700': locale === 'vi' }"
                    @click="setLocale('vi')"
                    >VI</Button
                >
            </div>
        </div>

        <!-- Main content -->
        <div class="mx-auto max-w-6xl px-4 pb-10">
            <div class="grid items-center gap-8 lg:grid-cols-2">
                <!-- Left: brand + hero -->
                <div class="hidden lg:block">
                    <h1
                        class="text-4xl font-bold tracking-tight text-slate-900"
                    >
                        {{ t('page.login.title') }}
                    </h1>
                    <p class="mt-4 text-slate-600 text-lg leading-relaxed">
                        {{ t('page.login.subtitle') }}
                    </p>
                    <div class="relative mt-8">
                        <div
                            class="absolute inset-0 -z-10 rounded-2xl bg-gradient-to-tr from-sky-100 to-indigo-100 blur-2xl"
                            aria-hidden="true"
                        ></div>
                        <img
                            src="/medee3.jpg"
                            alt="Healthcare illustration"
                            class="rounded-xl border shadow-lg ring-1 ring-black/5"
                        />
                    </div>
                </div>

                <!-- Right: auth card -->
                <div class="flex items-center justify-center mt-20">
                    <Card
                        class="w-full max-w-md shadow-xl border-0 ring-1 ring-black/5"
                    >
                        <CardHeader>
                            <CardTitle class="text-center text-2xl">{{
                                formTitle
                            }}</CardTitle>
                        </CardHeader>

                        <CardContent class="space-y-6">
                            <!-- Role (Patient / Doctor) -->
                            <div class="space-y-2">
                                <Label
                                    class="text-sm font-medium text-gray-700"
                                >
                                    {{ t('page.login.label.role') || 'Role' }}
                                </Label>
                                <Tabs v-model="role" class="w-full">
                                    <TabsList class="grid w-full grid-cols-2">
                                        <TabsTrigger value="patient">{{
                                            t('page.login.role.patient') ||
                                            'Patient'
                                        }}</TabsTrigger>
                                        <TabsTrigger value="doctor">{{
                                            t('page.login.role.doctor') ||
                                            'Doctor'
                                        }}</TabsTrigger>
                                    </TabsList>

                                    <!-- Patient form -->
                                    <TabsContent
                                        value="patient"
                                        class="mt-4 space-y-4"
                                    >
                                        <div class="space-y-2">
                                            <Label for="username">{{
                                                t('page.login.label.username')
                                            }}</Label>
                                            <Input
                                                id="username"
                                                v-model="username"
                                                type="text"
                                                autocomplete="username"
                                                required
                                                @input="resetError"
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
                                                autocomplete="current-password"
                                                required
                                                @input="resetError"
                                            />
                                        </div>

                                        <!-- Only show confirm on register -->
                                        <div
                                            v-if="mode === 'register'"
                                            class="space-y-2"
                                        >
                                            <Label for="confirmPassword">
                                                {{
                                                    t(
                                                        'page.login.label.confirm_password'
                                                    ) || 'Confirm Password'
                                                }}
                                            </Label>
                                            <Input
                                                id="confirmPassword"
                                                v-model="confirmPassword"
                                                type="password"
                                                autocomplete="new-password"
                                                required
                                                @input="resetError"
                                            />
                                        </div>
                                    </TabsContent>

                                    <!-- Doctor form -->
                                    <TabsContent
                                        value="doctor"
                                        class="mt-4 space-y-4"
                                    >
                                        <div class="space-y-2">
                                            <Label for="username-doctor">{{
                                                t('page.login.label.username')
                                            }}</Label>
                                            <Input
                                                id="username-doctor"
                                                v-model="username"
                                                type="text"
                                                autocomplete="username"
                                                required
                                                @input="resetError"
                                            />
                                        </div>
                                        <div class="space-y-2">
                                            <Label for="password-doctor">{{
                                                t('page.login.label.password')
                                            }}</Label>
                                            <Input
                                                id="password-doctor"
                                                v-model="password"
                                                type="password"
                                                autocomplete="current-password"
                                                required
                                                @input="resetError"
                                            />
                                        </div>

                                        <!-- Example: add doctor-only fields here later (e.g., license number) -->

                                        <div
                                            v-if="mode === 'register'"
                                            class="space-y-2"
                                        >
                                            <Label for="confirmPassword-doctor">
                                                {{
                                                    t(
                                                        'page.login.label.confirm_password'
                                                    ) || 'Confirm Password'
                                                }}
                                            </Label>
                                            <Input
                                                id="confirmPassword-doctor"
                                                v-model="confirmPassword"
                                                type="password"
                                                autocomplete="new-password"
                                                required
                                                @input="resetError"
                                            />
                                        </div>
                                        <div
                                            v-if="mode === 'register'"
                                            class="space-y-2 mt-2"
                                        >
                                            <Label>{{
                                                t('page.login.label.address')
                                            }}</Label>
                                            <Select v-model="doctorAddress">
                                                <SelectTrigger>
                                                    <SelectValue
                                                        :placeholder="
                                                            t(
                                                                'page.login.placeholder.choose_address'
                                                            )
                                                        "
                                                    />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="Hà Nội"
                                                        >Hà Nội</SelectItem
                                                    >
                                                </SelectContent>
                                            </Select>
                                        </div>
                                        <div
                                            v-if="mode === 'register'"
                                            class="space-y-2"
                                        >
                                            <Label>{{
                                                t('page.login.label.hospital')
                                            }}</Label>
                                            <Select
                                                v-model="doctorFacility"
                                                :disabled="!doctorAddress"
                                            >
                                                <SelectTrigger>
                                                    <SelectValue
                                                        :placeholder="
                                                            t(
                                                                'page.login.placeholder.choose_hospital'
                                                            )
                                                        "
                                                    />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem
                                                        value="Bệnh Viện Bạch Mai"
                                                        >Bệnh Viện Bạch
                                                        Mai</SelectItem
                                                    >
                                                </SelectContent>
                                            </Select>
                                        </div></TabsContent
                                    >
                                </Tabs>
                            </div>

                            <p v-if="error" class="text-sm text-red-600">
                                {{ error }}
                            </p>
                        </CardContent>

                        <CardFooter class="grid grid-rows-2 gap-2 mt-2">
                            <Button
                                type="button"
                                class="w-full"
                                :disabled="loading"
                                @click="handleSubmit"
                            >
                                <span v-if="!loading">
                                    {{
                                        mode === 'login'
                                            ? t('page.login.button.login')
                                            : t('page.login.button.register')
                                    }}
                                </span>
                                <span v-else>{{
                                    t('page.login.button.loading')
                                }}</span>
                            </Button>

                            <Button
                                variant="secondary"
                                @click="
                                    mode =
                                        mode === 'login' ? 'register' : 'login'
                                "
                            >
                                <span>
                                    {{
                                        mode === 'login'
                                            ? t('page.login.button.register')
                                            : t('page.login.button.login')
                                    }}
                                </span>
                            </Button>
                        </CardFooter>
                    </Card>
                </div>
            </div>
        </div>
    </div>
</template>
