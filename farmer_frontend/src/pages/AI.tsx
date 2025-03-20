import React, { useState, useEffect, useRef } from "react";
import Header from "../components/Header";
import BottomNav from "../components/BottomNav";

// Define a simple type for chat messages.
interface ChatMessage {
  text: string;
  sender: string;
  time: string;
}

const AI: React.FC = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    { text: "Hello!", sender: "You", time: "10:00" },
    { text: "Hi there!", sender: "Bot", time: "10:01" }
  ]);

  // WebSocket and MediaRecorder references.
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // Set up the WebSocket connection.
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "vad") {
          console.log("VAD status:", data.status);
        } else if (data.type === "transcription") {
          console.log("Transcription received:", data.text);
          setMessages((prev) => [
            ...prev,
            { text: data.text, sender: "Bot (transcription)", time: new Date().toLocaleTimeString() }
          ]);
        } else if (data.type === "chat_response") {
          console.log("Chat response received:", data.text);
          setMessages((prev) => [
            ...prev,
            { text: data.text, sender: "Bot", time: new Date().toLocaleTimeString() }
          ]);
        } else {
          console.log("Unknown message type:", data);
        }
      } catch (err) {
        console.error("Error parsing WebSocket message:", err);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = (event) => {
      console.log("WebSocket closed", event);
      wsRef.current = null;
    };

    return () => {
      // Close the WebSocket gracefully.
      try {
        ws.close();
      } catch (e) {
        console.error("Error closing WebSocket:", e);
      }
    };
  }, []);

  // Start recording audio and send chunks over WebSocket.
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(event.data);
        }
      };

      // Start recording with chunks every 100ms.
      recorder.start(100);
      console.log("Recording started");
    } catch (err) {
      console.error("Error accessing microphone:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      console.log("Recording stopped");
    }
  };

  const handleSend = () => {
    if (input.trim() === "") return;
    const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setMessages((prev) => [...prev, { text: input, sender: "You", time: now }]);
    // Optionally call your text chat API endpoint here.
    setInput("");
  };

  return (
    <div style={styles.container}>
      <Header />
      <div style={styles.chatArea}>
        {messages.map((message, index) => (
          <div
            key={index}
            style={{
              ...styles.chatMessage,
              ...(message.sender === "You" ? styles.userMessage : styles.otherMessage)
            }}
          >
            <div style={styles.messageText}>{message.text}</div>
            <div style={styles.messageFooter}>
              <span style={styles.messageTime}>{message.time}</span>
              <span style={styles.messageSender}>{message.sender}</span>
            </div>
          </div>
        ))}
      </div>
      <div style={styles.inputWrapper}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button style={styles.voiceBtn} onClick={startRecording}>
          🎤 Start Voice
        </button>
        <button style={styles.voiceBtn} onClick={stopRecording}>
          ✋ Stop Voice
        </button>
        <button style={styles.sendBtn} onClick={handleSend}>
          ➤ Send
        </button>
      </div>
      <BottomNav />
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: "flex",
    flexDirection: "column" as "column",
    minHeight: "100vh",
    backgroundColor: "#f5f5f5",
    paddingBottom: "80px"
  },
  chatArea: {
    flex: 1,
    padding: "16px",
    overflowY: "auto" as "auto"
  },
  inputWrapper: {
    position: "fixed" as "fixed",
    left: "0",
    right: "0",
    padding: "12px 16px",
    backgroundColor: "#fff",
    borderTop: "1px solid #ddd",
    display: "flex",
    gap: "8px",
    zIndex: 15,
    marginBottom: "24px"
  },
  input: {
    flex: 1,
    padding: "12px 16px",
    borderRadius: "9999px",
    border: "1px solid #ccc",
    fontSize: "14px",
    fontFamily: "Poppins, sans-serif"
  },
  voiceBtn: {
    padding: "15px",
    borderRadius: "50%",
    backgroundColor: "#eee",
    border: "none",
    cursor: "pointer",
    fontSize: "18px"
  },
  sendBtn: {
    padding: "15px",
    borderRadius: "50%",
    backgroundColor: "#1F3A93",
    color: "#fff",
    border: "none",
    cursor: "pointer",
    fontSize: "18px"
  },
  chatMessage: {
    display: "flex",
    flexDirection: "column" as "column",
    padding: "10px 16px",
    backgroundColor: "#fff",
    borderRadius: "12px",
    marginBottom: "12px",
    maxWidth: "70%",
    boxShadow: "0px 2px 5px rgba(0, 0, 0, 0.1)"
  },
  messageText: {
    fontSize: "16px",
    color: "#333",
    lineHeight: "1.4"
  },
  messageFooter: {
    display: "flex",
    justifyContent: "space-between",
    marginTop: "8px"
  },
  messageTime: {
    fontSize: "12px",
    color: "#aaa"
  },
  messageSender: {
    fontSize: "12px",
    color: "#aaa"
  },
  userMessage: {
    backgroundColor: "#fff",
    alignSelf: "flex-end",
    marginLeft: "auto"
  },
  otherMessage: {
    backgroundColor: "#f0f0f0",
    alignSelf: "flex-start"
  }
};

export default AI;
