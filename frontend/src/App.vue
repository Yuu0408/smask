<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import PatientFormModal from "./components/PatientFormModal.vue";
import Navbar from "./components/Navbar.vue";
import Sidebar from "./components/Sidebar.vue";
import { markFormAsSubmitted } from "./router";

import { useI18n } from "vue-i18n";
const { locale } = useI18n();

const chatPageRef = ref();
const sidebarOpen = ref(false);
function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value;
}
function handleNavigation(section: string) {
  console.log("Navigated to:", section);
}

const hasSubmittedForm = ref(false);
const route = useRoute();

function handleFormSubmitted(formData: any) {
  hasSubmittedForm.value = true;

  if (formData && chatPageRef.value) {
    markFormAsSubmitted();

    const greeting = locale.value === "vi" ? "Xin chào!" : "Hello!";
    chatPageRef.value.sendMessage(greeting);
  }
}

function handleFormFailed(error: any) {
  alert("Failed to submit patient info.");
  console.error(error);
}
</script>

<template>
  <Sidebar :isOpen="sidebarOpen" @navigate="handleNavigation" />
  <Navbar />

  <!-- TOGGLE BUTTON -->
  <button
    @click="toggleSidebar"
    class="fixed top-4 left-4 z-50 px-3 py-1 rounded shadow transition-colors"
    :class="[
      sidebarOpen
        ? 'bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700'
        : 'bg-gray-100 dark:bg-gray-900 hover:bg-gray-200 dark:hover:bg-gray-800',
    ]"
  >
    ☰
  </button>

  <!-- Main content area: fixed height, scroll only here -->
  <div
    :class="[
      'mt-16 transition-all duration-300',
      sidebarOpen ? 'ml-64' : 'ml-0',
    ]"
    class="flex flex-col items-center h-[calc(100vh-4rem)] overflow-y-auto"
    style="height: calc(100vh - 4rem)"
  >
    <router-view v-slot="{ Component }">
      <component
        :is="Component"
        ref="chatPageRef"
        :sidebar-open="sidebarOpen"
        v-bind="
          route.path === '/chat'
            ? {
                /* sendMessage and messages if needed */
              }
            : {}
        "
      />
    </router-view>
  </div>

  <PatientFormModal
    v-if="!hasSubmittedForm"
    @submitted="handleFormSubmitted"
    @failed="handleFormFailed"
  />
</template>
