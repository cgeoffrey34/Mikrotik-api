<template>
  <div class="card p-6">
    <div class="flex items-center">
      <div class="flex-shrink-0">
        <div :class="[iconBgClass, 'rounded-lg p-3']">
          <component :is="icon" class="h-6 w-6 text-white" />
        </div>
      </div>
      <div class="ml-5 w-0 flex-1">
        <dl>
          <dt class="text-sm font-medium text-gray-500 truncate">{{ title }}</dt>
          <dd class="flex items-baseline">
            <div class="text-2xl font-semibold text-gray-900">{{ value }}</div>
            <div v-if="suffix" class="ml-2 text-sm text-gray-500">{{ suffix }}</div>
          </dd>
        </dl>
      </div>
    </div>
    <div v-if="progress !== null" class="mt-4">
      <div class="flex items-center justify-between text-sm">
        <span class="text-gray-500">{{ progressLabel }}</span>
        <span class="font-medium" :class="progressColorClass">{{ progress }}%</span>
      </div>
      <div class="mt-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-300"
          :class="progressBarClass"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  value: [String, Number],
  suffix: String,
  icon: Object,
  color: {
    type: String,
    default: 'blue'
  },
  progress: {
    type: Number,
    default: null
  },
  progressLabel: String
})

const iconBgClass = computed(() => {
  const colors = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500',
    indigo: 'bg-indigo-500'
  }
  return colors[props.color] || colors.blue
})

const progressBarClass = computed(() => {
  if (props.progress > 80) return 'bg-red-500'
  if (props.progress > 60) return 'bg-yellow-500'
  return 'bg-green-500'
})

const progressColorClass = computed(() => {
  if (props.progress > 80) return 'text-red-600'
  if (props.progress > 60) return 'text-yellow-600'
  return 'text-green-600'
})
</script>
