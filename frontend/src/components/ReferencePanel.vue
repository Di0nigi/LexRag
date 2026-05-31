<template>
  <div class="reference-panel">

    <h2>Retrieved References</h2>

    <div
      v-for="reference in references"
      :key="reference.title"
      class="reference-card"
      @click="$emit('select', reference)"
    >
      

        <h3>{{ reference.title }}</h3>

        <p class="court-name">
          {{ reference.court }}
        </p>

        <p class="snippet">
          {{ reference.snippet + "..." }}
        </p>

        <p class="score-badge">
          Score: {{ reference.score }}
        </p>

      
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue';



function openReference(reference) {
  selectedReference.value = reference;
}


defineProps({
  references: Array,
  reasoningPath: Array
});

</script>

<style scoped>

.reference-panel {
  width: 39vw;
  height: 100vh;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  padding: 10px;
  padding-bottom: 3px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #1f2937;
  overflow-y: scroll;
}

h2 {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin-bottom: 16px;
  color: #111827;
}

/* Remove default anchor styling */
.reference-card-link {
  text-decoration: none;
  color: inherit;
}

.reference-card {
  background-color: #f9fafb;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #f3f4f6;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    border-color 0.2s ease;
  cursor: pointer;
}

.reference-card:hover {
  transform: translateY(-2px);
  border-color: #c7d2fe;
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
}

h3 {
  font-size: 1rem;
  margin: 0 0 4px 0;
  color: #0e3a9a;
}

.court-name {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #9ca3af;
  margin-bottom: 12px;
}

.snippet {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #374151;
  font-style: italic;
}

.score-badge {
  display: inline-block;
  margin-top: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #ecfdf5;
  color: #059669;
  padding: 2px 8px;
  border-radius: 99px;
}

</style>