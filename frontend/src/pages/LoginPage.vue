<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
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
import { Sparkles, User } from 'lucide-vue-next';
import ChatMultipleChoices from '@/components/ChatMultipleChoices.vue';
import ChatInput from '@/components/ChatInput.vue';

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

type PreviewMessage = { role: 'ai' | 'human'; text: string };
const sampleMessages = computed<PreviewMessage[]>(() => [
    { role: 'ai', text: t('page.login.example.messages.ai1') as string },
    { role: 'human', text: t('page.login.example.messages.human1') as string },
    { role: 'ai', text: t('page.login.example.messages.ai2') as string },
]);

const sampleChoices = [
    t('page.login.example.choice1') as string,
    t('page.login.example.choice2') as string,
    t('page.login.example.choice3') as string,
];

const slides = [
    { key: 'icon', type: 'icon' as const },
    { key: 'chat', type: 'chat' as const },
];

const currentSlide = ref(0);
let slideTimer: number | undefined;

onMounted(() => {
    slideTimer = window.setInterval(() => {
        currentSlide.value = (currentSlide.value + 1) % slides.length;
    }, 6000);
});

onUnmounted(() => {
    if (slideTimer) {
        clearInterval(slideTimer);
    }
});

function goToSlide(idx: number) {
    currentSlide.value = idx;
}

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
        class="relative min-h-screen overflow-hidden bg-gradient-to-br from-primary/8 via-white to-accent/10"
    >
        <div
            class="pointer-events-none absolute inset-0 opacity-70"
            aria-hidden="true"
        >
            <div
                class="absolute -left-32 top-10 size-96 rounded-full bg-primary/15 blur-3xl"
            />
            <div
                class="absolute right-10 top-24 size-80 rounded-full bg-accent/20 blur-3xl"
            />
        </div>

        <div class="relative mx-auto max-w-6xl px-4 py-14 space-y-12">
            <div
                class="flex items-center justify-between rounded-2xl border border-primary/10 bg-white/60 px-4 py-3 shadow-sm backdrop-blur"
            >
                <div class="flex items-center gap-2">
                    <span class="text-lg font-semibold tracking-tight text-primary"
                        >Medee</span
                    >
                    <span
                        class="rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-[0.2em] text-primary"
                        >Clinical AI</span
                    >
                </div>
                <div class="flex items-center gap-1">
                    <Button
                        size="sm"
                        variant="ghost"
                        :class="{ 'bg-primary/15 text-primary': locale === 'en' }"
                        @click="setLocale('en')"
                        >EN</Button
                    >
                    <Button
                        size="sm"
                        variant="ghost"
                        :class="{ 'bg-primary/15 text-primary': locale === 'vi' }"
                        @click="setLocale('vi')"
                        >VI</Button
                    >
                </div>
            </div>

            <div class="text-center space-y-4 pt-2">
                <h1 class="text-4xl font-bold leading-tight tracking-tight text-slate-900">
                    {{ t('page.login.title') }}
                </h1>
                <p class="text-lg leading-relaxed text-slate-600 max-w-3xl mx-auto">
                    {{ t('page.login.subtitle') }}
                </p>
            </div>

            <div class="grid grid-cols-1 gap-12 items-center md:grid-cols-2">
                <div class="flex justify-center">
                    <div
                        class="relative w-full max-w-xl overflow-hidden rounded-3xl border border-primary/15 bg-white/95 shadow-xl shadow-primary/10 backdrop-blur min-h-[440px]"
                    >
                        <Transition name="slide-wipe" mode="out-in">
                            <div
                                v-if="slides[currentSlide].type === 'icon'"
                                key="icon"
                                class="absolute inset-0 flex h-full min-h-[440px] items-center justify-center p-6"
                            >
                                <img
                                    src="/medee3.jpg"
                                    alt="Medee"
                                    class="h-[340px] w-auto rounded-2xl border border-primary/15 shadow-2xl shadow-primary/10 object-contain bg-white/70"
                                    draggable="false"
                                />
                            </div>
                            <div
                                v-else
                                key="chat"
                                class="absolute inset-0 flex h-full min-h-[440px] flex-col space-y-3 p-5"
                            >
                                <div class="flex items-center justify-end">
                                    <span
                                        class="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary"
                                    >
                                        <Sparkles class="size-4" />
                                        {{ t('chat.session.live') }}
                                    </span>
                                </div>
                                <div class="space-y-3">
                                    <div
                                        v-for="(msg, idx) in sampleMessages"
                                        :key="idx"
                                        class="flex items-start gap-2"
                                        :class="msg.role === 'human' ? 'justify-end' : 'justify-start'"
                                    >
                                        <div v-if="msg.role === 'ai'" class="flex-shrink-0 pt-1">
                                            <div
                                                class="flex size-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary/15 to-accent/20 text-primary shadow-sm"
                                            >
                                                <User class="size-4" aria-hidden="true" />
                                            </div>
                                        </div>
                                        <div
                                            class="max-w-[78%] rounded-2xl border px-4 py-3 text-sm shadow-sm"
                                            :class="
                                                msg.role === 'human'
                                                    ? 'bg-primary text-primary-foreground border-primary/20 shadow-primary/20 shadow-lg'
                                                    : 'bg-white text-foreground border-primary/10'
                                            "
                                        >
                                            {{ msg.text }}
                                        </div>
                                        <div v-if="msg.role === 'human'" class="flex-shrink-0 pt-1">
                                            <div
                                                class="flex size-9 items-center justify-center rounded-xl bg-muted text-foreground shadow-sm"
                                            >
                                                <User class="size-4" aria-hidden="true" />
                                            </div>
                                        </div>
                                    </div>

                                    <div class="pointer-events-none opacity-80">
                                        <ChatMultipleChoices :choices="sampleChoices" />
                                    </div>

                                    <div class="pointer-events-none opacity-80">
                                        <ChatInput :loading="false" />
                                    </div>
                                </div>
                            </div>
                        </Transition>

                        <div class="absolute inset-x-0 bottom-3 flex justify-center gap-2 z-10">
                            <button
                                v-for="(slide, idx) in slides"
                                :key="slide.key"
                                type="button"
                                class="h-2.5 w-2.5 rounded-full transition"
                                :class="currentSlide === idx ? 'bg-primary' : 'bg-muted'"
                                @click="goToSlide(idx)"
                            ></button>
                        </div>
                    </div>
                </div>

                <div class="flex items-start justify-center">
                    <Card
                        class="w-full max-w-md overflow-hidden rounded-3xl border border-primary/15 bg-white/95 shadow-2xl shadow-primary/15 backdrop-blur"
                    >
                        <form @submit.prevent="handleSubmit">
                        <CardHeader class="space-y-1 border-b border-border/70">
                            <p
                                class="text-[11px] uppercase tracking-[0.2em] text-muted-foreground"
                            >
                                {{ t('page.login.secureAccess') }}
                            </p>
                            <CardTitle class="text-2xl font-semibold">{{
                                formTitle
                            }}</CardTitle>
                        </CardHeader>

                        <CardContent class="space-y-6 pt-6">
                            <div class="space-y-2">
                                <Label
                                    class="text-sm font-medium text-foreground"
                                >
                                    {{
                                        mode === 'login'
                                            ? t(
                                                  'page.login.label.role_login'
                                              ) ||
                                              t('page.login.label.role') ||
                                              'Login as'
                                            : t(
                                                  'page.login.label.role_register'
                                              ) || 'Register as'
                                    }}
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

                        <CardFooter class="grid grid-rows-2 gap-2 border-t border-border/70 bg-white/70 p-4">
                            <Button
                                type="submit"
                                class="w-full rounded-xl shadow-md shadow-primary/15"
                                :disabled="loading"
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
                                type="button"
                                variant="secondary"
                                class="rounded-xl"
                                @click="mode = mode === 'login' ? 'register' : 'login'"
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
                        </form>
                    </Card>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.slide-wipe-enter-active,
.slide-wipe-leave-active {
    transition: transform 0.6s ease, opacity 0.6s ease;
}
.slide-wipe-enter-from {
    transform: translateX(20%);
    opacity: 0;
}
.slide-wipe-leave-to {
    transform: translateX(-20%);
    opacity: 0;
}
</style>

