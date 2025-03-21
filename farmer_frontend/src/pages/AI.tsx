import React, { useEffect, useRef, useState } from "react";
import Header from "../components/Header";
import BottomNav from "../components/BottomNav";

// Define a simple type for chat messages.
interface ChatMessage {
  text: string;
  sender: string;
  time: string;
}

export default function App() {
  /*** Realtime Session States & Refs ***/
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [events, setEvents] = useState<any[]>([]);
  const [dataChannel, setDataChannel] = useState<RTCDataChannel | null>(null);
  const peerConnection = useRef<RTCPeerConnection | null>(null);
  const audioElement = useRef<HTMLAudioElement | null>(null);

  /*** Chat States & Refs ***/
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    { text: "Hello!", sender: "You", time: "10:00" },
    { text: "Hi there!", sender: "Bot", time: "10:01" }
  ]);
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  /*** Realtime Session Functions ***/
  async function startSession() {
    // Get an ephemeral key from your server
    const tokenResponse = await fetch("http://localhost:8000/session");
    const data = await tokenResponse.json();
    const EPHEMERAL_KEY = data.client_secret.value;

    // Create a peer connection
    const pc = new RTCPeerConnection();
    peerConnection.current = pc;

    // Set up to play remote audio from the model
    const audioEl = document.createElement("audio");
    audioEl.autoplay = true;
    audioElement.current = audioEl;
    pc.ontrack = (e) => {
      audioEl.srcObject = e.streams[0];
    };

    // Add local audio track for microphone input
    const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
    pc.addTrack(ms.getTracks()[0]);

    // Set up data channel for sending and receiving events
    const dc = pc.createDataChannel("oai-events");
    dc.addEventListener("message", (e) => {
      console.log("DataChannel message:", e.data);
    });
    setDataChannel(dc);

    // Start the session using SDP
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    const baseUrl = "https://api.openai.com/v1/realtime";
    const model = "gpt-4o-realtime-preview-2024-12-17";
    const sdpResponse = await fetch(`${baseUrl}?model=${model}`, {
      method: "POST",
      body: offer.sdp,
      headers: {
        Authorization: `Bearer ${EPHEMERAL_KEY}`,
        "Content-Type": "application/sdp"
      }
    });

    const answer: RTCSessionDescriptionInit = {
      type: "answer",
      sdp: await sdpResponse.text()
    };
    await pc.setRemoteDescription(answer);
  }

  function stopSession() {
    if (dataChannel) {
      dataChannel.close();
    }
    if (peerConnection.current) {
      peerConnection.current.getSenders().forEach((sender) => {
        if (sender.track) {
          sender.track.stop();
        }
      });
      peerConnection.current.close();
    }
    setIsSessionActive(false);
    setDataChannel(null);
    peerConnection.current = null;
  }

  // Send an event to the realtime model
  function sendClientEvent(message: any) {
    if (dataChannel) {
      const timestamp = new Date().toLocaleTimeString();
      message.event_id = message.event_id || crypto.randomUUID();
      // send event (without timestamp as backend might not expect it)
      dataChannel.send(JSON.stringify(message));
      if (!message.timestamp) {
        message.timestamp = timestamp;
      }
      setEvents((prev) => [message, ...prev]);
    } else {
      console.error("Failed to send message - no data channel available", message);
    }
  }

  // Send a text message event to the realtime model
  function sendTextMessage(message: string) {
    const event = {
      type: "conversation.item.create",
      item: {
        type: "message",
        role: "user",
        content: [
          {
            type: "input_text",
            text: message
          }
        ]
      }
    };
    sendClientEvent(event);
    // Optionally, trigger a response event
    sendClientEvent({ type: "response.create" });
  }

  // Attach event listeners to the data channel when available
  useEffect(() => {
    if (dataChannel) {
      dataChannel.addEventListener("message", (e) => {
        const event = JSON.parse(e.data);
        if (!event.timestamp) {
          event.timestamp = new Date().toLocaleTimeString();
        }
        setEvents((prev) => [event, ...prev]);
      });
      dataChannel.addEventListener("open", () => {
        setIsSessionActive(true);
        setEvents([]);
      });
    }
  }, [dataChannel]);

  /*** WebSocket & MediaRecorder (Chat/Voice) ***/
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
            {
              text: data.text,
              sender: "Bot (transcription)",
              time: new Date().toLocaleTimeString()
            }
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
      try {
        ws.close();
      } catch (e) {
        console.error("Error closing WebSocket:", e);
      }
    };
  }, []);

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

      // Start recording with 100ms chunks.
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
    setMessages((prev) => [
      ...prev,
      { text: input, sender: "You", time: now }
    ]);
    // Optionally, also send via realtime session:
    sendTextMessage(input);
    setInput("");
  };

  /*** Combined UI ***/
  return (
    <div style={styles.container}>
      <Header />
      <div style={styles.mainContent}>
        {/* Left side: Realtime Session Console */}
        <div style={styles.sessionArea}>
          <h2>Realtime Session Console</h2>
          <div style={styles.sessionButtons}>
            <button
              onClick={startSession}
              style={styles.button}
              disabled={isSessionActive}
            >
              Start Session
            </button>
            {isSessionActive && (
              <button onClick={stopSession} style={styles.button}>
                Stop Session
              </button>
            )}
          </div>
          <div style={styles.eventsArea}>
            <h3>Session Events</h3>
            {events.map((event, index) => (
              <div key={index} style={styles.eventItem}>
                {JSON.stringify(event)}
              </div>
            ))}
          </div>
        </div>
        {/* Right side: Chat & Voice Interface */}
        <div style={styles.chatContainer}>
          <div style={styles.chatArea}>
            {messages.map((message, index) => (
              <div
                key={index}
                style={{
                  ...styles.chatMessage,
                  ...(message.sender === "You"
                    ? styles.userMessage
                    : styles.otherMessage)
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
        </div>
      </div>
      <BottomNav />
    </div>
  );
}

/*** Styles ***/
const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: "flex",
    flexDirection: "column",
    minHeight: "100vh",
    backgroundColor: "#f5f5f5",
    paddingBottom: "80px"
  },
  mainContent: {
    display: "flex",
    flex: 1,
    paddingTop: "60px" // Adjust if Header is fixed
  },
  sessionArea: {
    flexBasis: "380px",
    padding: "16px",
    borderRight: "1px solid #ddd",
    overflowY: "auto"
  },
  sessionButtons: {
    display: "flex",
    gap: "8px",
    marginBottom: "16px"
  },
  button: {
    padding: "10px 16px",
    backgroundColor: "#1F3A93",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer"
  },
  eventsArea: {
    maxHeight: "300px",
    overflowY: "auto",
    backgroundColor: "#fff",
    padding: "8px",
    borderRadius: "4px",
    boxShadow: "0px 2px 5px rgba(0, 0, 0, 0.1)"
  },
  eventItem: {
    padding: "4px 0",
    borderBottom: "1px solid #eee",
    fontSize: "12px"
  },
  chatContainer: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    position: "relative"
  },
  chatArea: {
    flex: 1,
    padding: "16px",
    overflowY: "auto"
  },
  inputWrapper: {
    position: "fixed",
    left: "380px",
    right: "0",
    bottom: "0",
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
    flexDirection: "column",
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
