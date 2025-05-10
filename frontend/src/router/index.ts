import { createRouter, createWebHistory } from "vue-router";
import ChatPage from '@/components/ChatPage.vue'
import TodoPage from '@/components/TodoPage.vue'
import MedicalRecord from "@/components/MedicalRecord.vue"
import DiagnosisPage from "@/components/DiagnosisPage.vue"

let hasSubmittedForm = false

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/chat' },
    { path: '/chat', component: ChatPage },
    { path: '/todo', component: TodoPage },
    { path: '/record', component: MedicalRecord },
    { path: '/diagnosis', component: DiagnosisPage },
  ],
})

// navigation guard
router.beforeEach((to, from, next) => {
  if (!hasSubmittedForm && to.path !== '/chat') {
    next('/chat') // redirect non-submitted user to /chat
  } else {
    next()
  }
})

// utility to mark form as submitted
export function markFormAsSubmitted() {
  hasSubmittedForm = true
}

export default router
