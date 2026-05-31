
<template>
  <div class="chat-page">
   
    <div class="historyCol">
      <div class="history-header">
        <h2>Chats</h2>
        
      </div>

      <div class="history-list">
        <div
          v-for="chat in chatHistory"
          :key="chat.id"
          :class="['history-item', activeChatId === chat.id ? 'active' : '']"
          @click="loadChat(chat.id)"
        >
          <div class="history-title">
            {{ chat.title }}
          </div>

          <div class="history-preview">
            {{ chat.preview }}
          </div>

          <div class="history-footer">
            <span>{{ formatDate(chat.updatedAt) }}</span>

            <button
              class="delete-btn"
              @click.stop="deleteChat(chat.id)"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

  
    <div class="chat-container">
      <div class="chat-header">
        <h1>Legal RAG Chatbot</h1>
      </div>

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
        <input
          v-model="userInput"
          placeholder="Ask a legal question..."
        />

        <button class="btn" type="submit">
          Send
        </button>

        <button
          class="btn"
          type="button"
          @click="startNewChat"
        >
          New Chat
        </button>
      </form>
    </div>


    <ReferencePanel 
    v-if="!selectedReference"
  :references="references"
  @select="selectedReference = $event"
    />

    <ReferenceDetailPanel
    v-if="selectedReference"
    :reference="selectedReference"
    @close="selectedReference = null"
    />
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted } from "vue";
import { marked } from "marked";
import DOMPurify from "dompurify";
import { sendChatMessage } from "../api/chatApi";
import ReferencePanel from "./ReferencePanel.vue";
import ReferenceDetailPanel from "./ReferenceDetailPanel.vue"

defineEmits(["select"]);

const selectedReference = ref(null);
 
const renderer = new marked.Renderer();

renderer.code = (code) => `<p>${code.text ?? code}</p>`;
renderer.codespan = (code) => code.text ?? code;

marked.setOptions({
  breaks: true,
  gfm: true,
  renderer
});

function renderMarkdown(text) {
  const raw = marked.parse(text ?? "");
  return DOMPurify.sanitize(raw);
}

const messagesContainer = ref(null);
const userInput = ref("");
const isLoading = ref(false);
const references = ref([]);
const reasoningPath = ref([]);

const activeChatId = ref(null);

const chatHistory = ref([]);

const defaultAssistantMessage = {
  id: 1,
  role: "assistant",
  text: "Hello. I can retrieve and explain legal cases."
};

const messages = ref([defaultAssistantMessage]);

function saveChatsToStorage() {
  localStorage.setItem(
    "legal-rag-chat-history",
    JSON.stringify(chatHistory.value)
  );
}

function loadChatsFromStorage() {
  const saved = localStorage.getItem("legal-rag-chat-history");

  if (saved) {
    chatHistory.value = JSON.parse(saved);

    if (chatHistory.value.length > 0) {
      loadChat(chatHistory.value[0].id);
    }
  }
}


function createChatObject(firstMessage = "New Chat") {
  return {
    id: Date.now(),
    title:
      firstMessage.length > 30
        ? `${firstMessage.slice(0, 30)}...`
        : firstMessage,
    preview: firstMessage,
    updatedAt: new Date().toISOString(),
    messages: [defaultAssistantMessage],
    references: [],
    reasoningPath: []
  };
}

function startNewChat() {
  const newChat = createChatObject();

  chatHistory.value.unshift(newChat);

  activeChatId.value = newChat.id;

  messages.value = [...newChat.messages];
  references.value = [];
  reasoningPath.value = [];
  userInput.value = "";

  saveChatsToStorage();
}

function loadChat(chatId) {
  const selectedChat = chatHistory.value.find(
    (chat) => chat.id === chatId
  );

  if (!selectedChat) return;

  activeChatId.value = selectedChat.id;

  messages.value = [...selectedChat.messages];
  references.value = [...selectedChat.references];
  reasoningPath.value = [...selectedChat.reasoningPath];

  scrollToBottom();
}

function updateCurrentChat() {
  const currentChat = chatHistory.value.find(
    (chat) => chat.id === activeChatId.value
  );

  if (!currentChat) return;

  currentChat.messages = [...messages.value];
  currentChat.references = [...references.value];
  currentChat.reasoningPath = [...reasoningPath.value];
  currentChat.updatedAt = new Date().toISOString();

  const firstUserMessage = messages.value.find(
    (message) => message.role === "user"
  );

  if (firstUserMessage) {
    currentChat.title =
      firstUserMessage.text.length > 30
        ? `${firstUserMessage.text.slice(0, 30)}...`
        : firstUserMessage.text;

    currentChat.preview = firstUserMessage.text;
  }

  saveChatsToStorage();
}

function deleteChat(chatId) {
  chatHistory.value = chatHistory.value.filter(
    (chat) => chat.id !== chatId
  );

  if (activeChatId.value === chatId) {
    if (chatHistory.value.length > 0) {
      loadChat(chatHistory.value[0].id);
    } else {
      startNewChat();
    }
  }

  saveChatsToStorage();
}

function formatDate(dateString) {
  const date = new Date(dateString);

  return date.toLocaleDateString([], {
    month: "short",
    day: "numeric"
  });
}


async function scrollToBottom() {
  await nextTick();

  if (messagesContainer.value) {
    messagesContainer.value.scrollTop =
      messagesContainer.value.scrollHeight;
  }
}

async function handleSend() {
  if (!userInput.value.trim()) return;

  // Create first chat automatically
  if (!activeChatId.value) {
    startNewChat();
  }

  const query = userInput.value;

  messages.value.push({
    id: Date.now(),
    role: "user",
    text: query
  });

  updateCurrentChat();

  await scrollToBottom();

  userInput.value = "";
  isLoading.value = true;

  try {
    const data = await sendChatMessage(query);

    console.log(data);

    messages.value.push({
      id: Date.now() + 1,
      role: "assistant",
      text: data.answer
    });

    references.value = data.references || [];
    reasoningPath.value = data.reasoning_path || [];

    updateCurrentChat();

    await scrollToBottom();
  } catch (error) {
    messages.value.push({
      id: Date.now() + 2,
      role: "assistant",
      text: "Error retrieving response."
    });

    updateCurrentChat();

    await scrollToBottom();
  } finally {
    isLoading.value = false;
  }
}

watch(messages, () => {
  updateCurrentChat();
}, { deep: true });

onMounted(() => {
  loadChatsFromStorage();

  if (chatHistory.value.length === 0) {
    startNewChat();
  }
});
</script>
<style scoped>

/* ───────────────────────────────
   GLOBAL LAYOUT
─────────────────────────────── */
.chat-page {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
  background: #f6f7fb;
}

/* ───────────────────────────────
   LEFT SIDEBAR (HISTORY)
─────────────────────────────── */
.historyCol {
  width: 280px;
  min-width: 240px;
  height: 100vh;

  background: #ffffff;
  border-right: 1px solid #e5e7eb;

  display: flex;
  flex-direction: column;

  color: #111827;
  overflow: hidden;

  box-shadow: 4px 0 12px rgba(0, 0, 0, 0.03);
}

.history-header {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;

  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-header h2 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #111827;
}

.new-chat-btn {
  border: none;
  border-radius: 10px;
  padding: 10px;

  cursor: pointer;

  background: #2563eb;
  color: white;
  font-weight: 600;

  transition: 0.2s ease;
}

.new-chat-btn:hover {
  background: #1d4ed8;
}

/* ───────────────────────────────
   CHAT HISTORY LIST
─────────────────────────────── */
.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.history-item {
  background: #f9fafb;

  border: 1px solid #eef2f7;
  border-radius: 12px;

  padding: 12px;
  margin-bottom: 10px;

  cursor: pointer;

  transition: all 0.2s ease;
}

.history-item:hover {
  transform: translateY(-1px);
  background: #f3f4f6;
  border-color: #dbeafe;
}

.history-item.active {
  background: #eaf2ff;
  border-color: #93c5fd;
}

.history-title {
  font-size: 0.92rem;
  font-weight: 600;

  margin-bottom: 6px;

  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;

  color: #111827;
}

.history-preview {
  font-size: 0.8rem;
  color: #6b7280;

  overflow: hidden;
  text-overflow: ellipsis;

  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.history-footer {
  margin-top: 10px;

  display: flex;
  justify-content: space-between;
  align-items: center;

  font-size: 0.75rem;
  color: #9ca3af;
}

.delete-btn {
  border: none;
  background: transparent;

  color: #9ca3af;
  cursor: pointer;

  font-size: 0.75rem;

  transition: 0.2s ease;
}

.delete-btn:hover {
  color: #ef4444;
}

/* ───────────────────────────────
   MAIN CHAT AREA
─────────────────────────────── */
.chat-container {
  display: flex;
  flex-direction: column;

  width: 50vw;
  height: 100vh;

  background: #ffffff;
  border-right: 1px solid #e5e7eb;
}

.chat-header {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  background: #ffffff;
}

.chat-header h1 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #111827;
}

/* ───────────────────────────────
   MESSAGES
─────────────────────────────── */
.messages {
  flex: 1;
  overflow-y: auto;

  padding: 16px;

  display: flex;
  flex-direction: column;

  background: #f9fafb;
}

/* chat bubbles */
.message {
  width: fit-content;
  max-width: 75%;

  padding: 10px 14px;
  border-radius: 14px;

  margin: 8px 0;

  line-height: 1.5;
  word-break: break-word;

  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.message.user {
  background: #2563eb;
  color: white;
  align-self: flex-end;
}

.message.assistant {
  background: white;
  color: #111827;
  align-self: flex-start;
  border: 1px solid #e5e7eb;
}

/* ───────────────────────────────
   INPUT AREA
─────────────────────────────── */
.input-area {
  display: flex;
  align-items: center;

  width: 50vw;
  height: 72px;

  padding: 2px;
  gap: 2px;

  border-top: 1px solid #e5e7eb;
  background: white;
}

input {
  flex: 1;

  padding: 10px 12px;

  border: 1px solid #e5e7eb;
  border-radius: 10px;

  outline: none;

  transition: 0.2s ease;
}

input:focus {
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.btn {
  min-width: 90px;

  border-radius: 10px;
  border: 1px solid #e5e7eb;

  background: #ffffff;

  cursor: pointer;

  transition: 0.2s ease;

  font-weight: 500;
}

.btn:hover {
  background: #f3f4f6;
}

/* ───────────────────────────────
   LOADING ANIMATION
─────────────────────────────── */
.loading {
  opacity: 0.6;
  animation: pulse 1.2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}

</style>