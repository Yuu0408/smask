<script setup lang="ts">
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

defineProps<{ title: string }>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="text-lg font-semibold">{{ title }}</CardTitle>
    </CardHeader>
    <CardContent class="space-y-2">
      <slot />
    </CardContent>
  </Card>
</template>
