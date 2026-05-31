<template>
  <div class="detail-panel">

    <div class="header">
      <div>
        <h1 class="title">{{ reference.title }}</h1>
        <p class="court">{{ reference.court }}</p>
      </div>

      <button class="close" @click="$emit('close')">
        ✕
      </button>
    </div>

    <div class="score-row">
      <span class="score">
        Confidence: {{ reference.score }}
      </span>
    </div>


    <div class="section">
      <h3>Full Text</h3>
      <p class="full-text">
        {{ reference.full|| "No additional text available." }}
      </p>
    </div>

    <div class="footer">
      <a
        :href="reference.url"
        target="_blank"
        rel="noopener noreferrer"
        class="source-link"
      >
        Open original source →
      </a>
    </div>

  </div>
</template>

<script setup>
defineProps({
  reference: Object
});

defineEmits(["close"]);
</script>

<style scoped>
.detail-panel {
  width: 100%;
  height: 100%;
  background: #ffffff;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  font-family: Inter, system-ui, sans-serif;
  color: #111827;
  overflow-y: auto;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 12px;
}

.title {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.3;
}

.court {
  font-size: 0.85rem;
  color: #6b7280;
  text-transform: uppercase;
  margin-top: 4px;
  letter-spacing: 0.05em;
}

/* Close button */
.close {
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  width: 36px;
  height: 36px;
  cursor: pointer;
  font-size: 16px;
  transition: 0.2s ease;
}

.close:hover {
  background: #e5e7eb;
}

/* Score badge */
.score-row {
  display: flex;
}

.score {
  background: #ecfdf5;
  color: #059669;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* Sections */
.section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section h3 {
  font-size: 0.9rem;
  color: #374151;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.snippet {
  background: #f9fafb;
  padding: 12px;
  border-radius: 10px;
  color: #374151;
  font-style: italic;
  line-height: 1.6;
}

.full-text {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  padding: 12px;
  border-radius: 10px;
  color: #111827;
  line-height: 1.6;
  
}

/* Footer */
.footer {
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #e5e7eb;
}

.source-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
}

.source-link:hover {
  text-decoration: underline;
}
</style>