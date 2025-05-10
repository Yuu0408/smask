// src/api/chatSocket.ts
type MessageCallback = (message: string) => void

let socket: WebSocket | null = null
let messageCallback: MessageCallback | null = null

export function connectToChatServer(onMessage: MessageCallback) {
  socket = new WebSocket('ws://localhost:8000/ws') // adjust as needed
  messageCallback = onMessage

  socket.addEventListener('open', () => {
    console.log('✅ WebSocket connected')
  })

  socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data)
    if (data.text && messageCallback) {
      messageCallback(data.text)
    }
  })

  socket.addEventListener('close', () => {
    console.log('❌ WebSocket disconnected')
  })
}

export function sendMessageToServer(text: string) {
  if (socket?.readyState === WebSocket.OPEN) {
    socket.send(text)
  } else {
    console.warn('WebSocket not connected.')
  }
}

export function disconnectFromChatServer() {
  socket?.close()
}
