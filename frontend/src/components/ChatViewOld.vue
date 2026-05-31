<template>
  <div class="chat-page">
    <div class="history-panel">
  <div class="history-header">
    <button @click="startNewChat">+ New Chat</button>
  </div>

  <div
    v-for="s in sessions"
    :key="s.id"
    class="session"
    :class="{ active: s.id === activeSessionId }"
    @click="switchSession(s.id)"
  >
    {{ s.title }}
  </div>
</div>
    <div class="chat-container">
      <h1>Legal RAG Chatbot</h1>

      <div class="messages" ref="messagesContainer">
        <div
          v-for="message in messages"
          :key="message.id"
          :class="['message', message.role]"
          v-html="renderMarkdown(message.text)"
        />
        <div v-if="isLoading" class="message assistant loading">
          Thinking...
          
        </div>
      </div>

      <form @submit.prevent="handleSend" class="input-area">
        <input v-model="userInput" placeholder="Ask a legal question..." />
        <button class="btn" type="submit">Send</button>
        <button class="btn" type="button" @click="startNewChat">New Chat</button>
      </form>
    </div>

    <ReferencePanel :references="references" :reasoningPath="reasoningPath" />
  </div>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { marked } from "marked";
import DOMPurify from "dompurify";
import { sendChatMessage } from "../api/chatApi";
import ReferencePanel from "./ReferencePanel.vue";
import { computed } from "vue";

const activeSession = computed(() =>
  sessions.value.find(s => s.id === activeSessionId.value)
);

const sessions = ref([
  {
    id: Date.now(),
    title: "New Chat",
    messages: [
      {
        id: 1,
        role: "assistant",
        text: "Hello. I can retrieve and explain legal cases."
      }
    ],
    references: [],
    reasoningPath: []
  }
]);



// Configure marked for clean output
const renderer = new marked.Renderer();
renderer.code = (code) => `<p>${code.text ?? code}</p>`;
renderer.codespan = (code) => code.text ?? code;



marked.setOptions({
  breaks: true,
  gfm: true,
  renderer,
});

function renderMarkdown(text) {
  const raw = marked.parse(text ?? "");
  const clean = DOMPurify.sanitize(raw);
  return clean;
}

const messagesContainer = ref(null);
const userInput = ref("");
const isLoading = ref(false);

const messages = ref([
  { id: 1, role: "assistant", text: "Hello. I can retrieve and explain legal cases." }
]);
const references = ref([]);
const reasoningPath = ref([]);

async function scrollToBottom() {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}

function startNewChat() {
  const newSession = {
    id: Date.now(),
    title: "New Chat",
    messages: [
      {
        id: 1,
        role: "assistant",
        text: "Hello. I can retrieve and explain legal cases."
      }
    ],
    references: [],
    reasoningPath: []
  };

  sessions.value.unshift(newSession);
  activeSessionId.value = newSession.id;
}
function switchSession(id) {
  activeSessionId.value = id;
}

async function handleSend() {
  if (!userInput.value.trim()) return;

  const query = userInput.value;

  activeSession.value.messages.push({
    id: Date.now(),
    role: "user",
    text: query
  });

  await scrollToBottom();

  userInput.value = "";
  isLoading.value = true;

  try {
    const data = await sendChatMessage(query);

    activeSession.value.messages.push({
      id: Date.now() + 1,
      role: "assistant",
      text: data.answer
    });

    activeSession.value.references = data.references;
    activeSession.value.reasoningPath = data.reasoning_path;

    await scrollToBottom();

  } catch {
    activeSession.value.messages.push({
      id: Date.now() + 2,
      role: "assistant",
      text: "Error retrieving response."
    });

    await scrollToBottom();

  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.history-panel {
  width: 20vw;
  height: 100vh;
  border-right: 1px solid #ddd;
  overflow-y: auto;
  padding: 10px;
}

.history-header {
  margin-bottom: 10px;
}

.session {
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 6px;
  background: #f8fafc;
}

.session.active {
  background: #dbeafe;
}

.chat-page {
  display: flex;
  width: 100vw;
  height: 100vh;
  gap: 0;
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.chat-container {
  display: flex;
  flex-direction: column;
  width: 60vw;
  height: 100vh;
  border: 1px solid #ddd;
  border-radius: 0px;
  padding: 0;
  margin: 0;
}

.messages {
  display: flex;
  flex-direction: column;
  width: 60vw;
  height: 80vh;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: transparent;
}


.message {
  /* Let content dictate width; cap at 75% of the chat pane */
  width: fit-content;
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 10px;
  margin: 10px;
  line-height: 1.5;
  word-break: break-word;
}

.message.user {
  background: #dbeafe;
  align-self: flex-end;
}

.message.assistant {
  background: #f3f4f6;
  align-self: flex-start;
}


.message :deep(p)          { margin: 0 0 0.5em; }
.message :deep(p:last-child){ margin-bottom: 0; }
.message :deep(ul),
.message :deep(ol)         { margin: 0.4em 0 0.4em 1.4em; padding: 0; }
.message :deep(li)         { margin-bottom: 0.2em; }
.message :deep(h1),
.message :deep(h2),
.message :deep(h3)         { margin: 0.6em 0 0.3em; line-height: 1.3; }
/* .message :deep(pre)        {
  background: rgba(0,0,0,0.07);
  border-radius: 6px;
  padding: 10px 12px;
  overflow-x: visible;
  white-space: pre-wrap; 
  word-break: break-word;
}
.message :deep(pre code) {
  background: none;
  padding: 0;
  white-space: pre-wrap;  
  word-break: break-word; 
} */
.message :deep(blockquote) {
  border-left: 3px solid #94a3b8;
  margin: 0.4em 0;
  padding-left: 0.8em;
  color: #475569;
}
.message :deep(a)          { color: #2563eb; text-decoration: underline; }
.message :deep(hr)         { border: none; border-top: 1px solid #cbd5e1; margin: 0.6em 0; }
.message :deep(table)      { border-collapse: collapse; width: 100%; margin: 0.5em 0; }
.message :deep(th),
.message :deep(td)         { border: 1px solid #cbd5e1; padding: 5px 8px; font-size: 0.9em; }
.message :deep(th)         { background: rgba(0,0,0,0.05); font-weight: 600; }

.loading {
  opacity: 0.7;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50%       { opacity: 1;   }
}

.input-area {
  align-self: flex-end;
  display: flex;
  flex-direction: row;
  width: 60vw;
  height: 6vh;
  gap: 0;
}

input {
  flex: 1;
  padding-left: 10px;
  padding-right: 10px;
  border: 1px solid #000;
  border-radius: 8px;
}

.btn {
  width: 5vw;
  height: 6vh;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #000;
  background: white;
  cursor: pointer;
}

.btn:hover { background: #f3f4f6; }
</style>