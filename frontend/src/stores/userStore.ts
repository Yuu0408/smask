import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Message } from '@/types/message'
import type { MedicalRecord } from '@/types/medicalRecord'
import type { DiagnosisPaper } from '@/types/diagnosisPaper'

export const useUserStore = defineStore('user', () => {
  const sessionId = ref<string | null>(null)
  const messages = ref<Message[]>([])
  const medicalRecord = ref<MedicalRecord | null>(null)
  const todo = ref<string[]>([])
  const diagnosis = ref<DiagnosisPaper | null>(null)

  function setSessionId(id: string) {
    sessionId.value = id
  }

  function addMessage(message: Message) {
    messages.value.push(message)
  }

  function clearMessages() {
    messages.value = []
  }

  function setMedicalRecord(record: MedicalRecord) {
    medicalRecord.value = record
  }

  function setTodo(list: string[]) {
    todo.value = list
  }

  function clearTodo() {
    todo.value = []
  }

  function setDiagnosis(diagnosisPaper: DiagnosisPaper) {
    diagnosis.value = diagnosisPaper
  }

  return {
    sessionId,
    setSessionId,
    messages,
    addMessage,
    clearMessages,
    medicalRecord,
    setMedicalRecord,
    todo,
    setTodo,
    clearTodo,
    diagnosis,
    setDiagnosis,
  }
})
