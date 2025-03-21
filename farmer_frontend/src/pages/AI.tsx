import React, {useEffect, useRef, useState} from "react";
import Header from "../components/Header";
import BottomNav from "../components/BottomNav";

interface ChatMessage {
    text: string;
    sender: string;
    time: string;
}

export default function App() {
    const [isSessionActive, setIsSessionActive] = useState(false);
    const [dataChannel, setDataChannel] = useState<RTCDataChannel | null>(null);
    const peerConnection = useRef<RTCPeerConnection | null>(null);
    const audioElement = useRef<HTMLAudioElement | null>(null);
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const wsRef = useRef<WebSocket | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);

    async function startSession() {
        const tokenResponse = await fetch("http://localhost:8000/session");
        const data = await tokenResponse.json();
        const EPHEMERAL_KEY = data.client_secret.value;
        const pc = new RTCPeerConnection();
        peerConnection.current = pc;
        const audioEl = document.createElement("audio");
        audioEl.autoplay = true;
        audioElement.current = audioEl;
        pc.ontrack = (e) => {
            audioEl.srcObject = e.streams[0];
        };
        const ms = await navigator.mediaDevices.getUserMedia({audio: true});
        pc.addTrack(ms.getTracks()[0]);
        const dc = pc.createDataChannel("oai-events");
        dc.addEventListener("message", (e) => {
            console.log("DataChannel message:", e.data);
        });
        setDataChannel(dc);
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        const sdpResponse = await fetch(`https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17`, {
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
        setIsSessionActive(true);
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

    const handleSend = () => {
        if (input.trim() === "") return;
        const now = new Date().toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});
        setMessages((prev) => [...prev, {text: input, sender: "You", time: now}]);
        setInput("");
    };

    const startRecording = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({audio: true});
        const recorder = new MediaRecorder(stream);
        mediaRecorderRef.current = recorder;
        recorder.ondataavailable = (event) => {
            if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send(event.data);
            }
        };
        recorder.start(100);
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
        }
    };

    return (
        <div style={styles.container}>
            <Header/>
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
                        placeholder="Message"
                    />
                    <button
                        style={isSessionActive ? styles.stopSessionBtn : styles.startSessionBtn}
                        onClick={isSessionActive ? stopSession : startSession}
                    >
                        {isSessionActive ? '⛔' : '▶'}
                    </button>
                    <button style={styles.voiceBtn} onClick={startRecording}>🎤</button>
                    <button style={styles.voiceBtn} onClick={stopRecording}>✋</button>
                    <button style={styles.sendBtn} onClick={handleSend}>➤</button>
                </div>
            </div>
            <BottomNav/>
        </div>
    );
}

const styles: { [key: string]: React.CSSProperties } = {
    container: {
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        backgroundColor: "#f5f5f5",
    },
    chatContainer: {
        flex: 1,
        display: "flex",
        flexDirection: "column",
        backgroundColor: "#ffffff",
        paddingTop: "70px",
        borderTopLeftRadius: "16px",
        borderTopRightRadius: "16px",
    },
    chatArea: {
        flex: 1,
        padding: "16px",
        overflowY: "auto",
        paddingBottom: "140px"
    },
    inputWrapper: {
        display: "flex",
        alignItems: "center",
        padding: "8px 8px 8px 12px",
        backgroundColor: "#fff",
        borderTop: "1px solid #ddd",
        gap: "6px",
        position: "fixed",
        bottom: "100px",
        left: "0",
        right: "0",
        zIndex: 99,
    },
    input: {
        flex: 1,
        padding: "10px 14px",
        borderRadius: "9999px",
        border: "1px solid #ccc",
        fontSize: "14px",
        fontFamily: "Poppins, sans-serif"
    },
    voiceBtn: {
        padding: "10px",
        borderRadius: "50%",
        backgroundColor: "#eee",
        border: "none",
        cursor: "pointer",
        fontSize: "14px",
        transition: "background 0.3s"
    },
    sendBtn: {
        padding: "10px",
        borderRadius: "50%",
        backgroundColor: "#1F3A93",
        color: "#fff",
        border: "none",
        cursor: "pointer",
        fontSize: "14px",
        transition: "background 0.3s"
    },
    startSessionBtn: {
        padding: "10px",
        borderRadius: "50%",
        backgroundColor: "#4CAF50",
        color: "#fff",
        border: "none",
        cursor: "pointer",
        fontSize: "14px",
        transition: "background 0.3s"
    },
    stopSessionBtn: {
        padding: "10px",
        borderRadius: "50%",
        backgroundColor: "#FF5252",
        color: "#fff",
        border: "none",
        cursor: "pointer",
        fontSize: "14px",
        transition: "background 0.3s"
    },
    chatMessage: {
        display: "flex",
        flexDirection: "column",
        padding: "10px 16px",
        backgroundColor: "#fff",
        borderRadius: "12px",
        marginBottom: "12px",
        maxWidth: "70%",
        boxShadow: "0px 2px 5px rgba(0, 0, 0, 0.05)"
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
        backgroundColor: "#e0f7fa",
        alignSelf: "flex-end",
        marginLeft: "auto"
    },
    otherMessage: {
        backgroundColor: "#f0f0f0",
        alignSelf: "flex-start"
    }
};
