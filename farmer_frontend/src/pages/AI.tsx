import React, {useState, useEffect} from "react";
import Header from "../components/Header";
import BottomNav from "../components/BottomNav";

const AI = () => {
    const [input, setInput] = useState("");
    const [bottomOffset, setBottomOffset] = useState(64);
    const [messages, setMessages] = useState([
        {text: "Hello!", sender: "You", time: "10:00"},
        {text: "Hi there!", sender: "Bot", time: "10:01"}
    ]);
    const chatAreaRef = React.useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        const initialHeight = window.innerHeight;

        const handleResize = () => {
            const heightDiff = initialHeight - window.innerHeight;
            if (heightDiff > 150) {
                setBottomOffset(heightDiff);
            } else {
                setBottomOffset(64);
            }
        };

        window.addEventListener("resize", handleResize);

        return () => window.removeEventListener("resize", handleResize);
    }, []);

    const getCurrentTime = () => {
        const now = new Date();
        return now.toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});
    };

    const handleSend = () => {
        if (input.trim() === "") return;
        console.log("Send message:", input);
        setMessages([...messages, {text: input, sender: "You", time: getCurrentTime()}]);
        setInput("");
    };

    const handleVoice = () => {
        console.log("Voice input triggered");
    };

    const handleClick = () => {
        window.scrollTo({
            top: document.documentElement.scrollHeight,
            behavior: "smooth",
        });
    };

    return (
        <div style={styles.container}>
            <Header/>
            <div style={styles.chatArea} ref={chatAreaRef}>
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
            <div
                style={{
                    ...styles.inputWrapper,
                    bottom: `${bottomOffset}px`,
                }}
            >
                <input
                    style={styles.input}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message..."
                    onClick={handleClick}
                />
                <button style={styles.voiceBtn} onClick={handleVoice}>
                    🎤
                </button>
                <button style={styles.sendBtn} onClick={handleSend}>
                    ➤
                </button>
            </div>

            <BottomNav/>
        </div>
    );
};

export default AI;

const styles: { [key: string]: React.CSSProperties } = {
    container: {
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        backgroundColor: "#f5f5f5",
        paddingBottom: "80px",
    },
    chatArea: {
        flex: 1,
        padding: "16px",
        overflowY: "auto",
    },
    inputWrapper: {
        position: "fixed",
        left: "0",
        right: "0",
        padding: "12px 16px",
        backgroundColor: "#fff",
        borderTop: "1px solid #ddd",
        display: "flex",
        gap: "8px",
        zIndex: 15,
        transition: "bottom 0.3s ease-in-out",
        marginBottom: "24px",
    },
    input: {
        flex: 1,
        padding: "12px 16px",
        borderRadius: "9999px",
        border: "1px solid #ccc",
        fontSize: "14px",
        fontFamily: "Poppins, sans-serif",
    },
    voiceBtn: {
        padding: "12px",
        borderRadius: "50%",
        backgroundColor: "#eee",
        border: "none",
        cursor: "pointer",
        fontSize: "18px",
    },
    sendBtn: {
        padding: "12px",
        borderRadius: "50%",
        backgroundColor: "#1F3A93",
        color: "#fff",
        border: "none",
        cursor: "pointer",
        fontSize: "18px",
    },
    chatMessage: {
        display: "flex",
        flexDirection: "column",
        padding: "10px 16px",
        backgroundColor: "#fff",
        borderRadius: "12px",
        marginBottom: "12px",
        maxWidth: "70%",
        boxShadow: "0px 2px 5px rgba(0, 0, 0, 0.1)",
    },
    messageText: {
        fontSize: "16px",
        color: "#333",
        lineHeight: "1.4",
    },
    messageFooter: {
        display: "flex",
        justifyContent: "space-between",
        marginTop: "4px",
    },
    messageTime: {
        fontSize: "12px",
        color: "#aaa",
    },
    messageSender: {
        fontSize: "12px",
        color: "#aaa",
    },
    userMessage: {
        backgroundColor: "#fff",
        color: "#fff",
        alignSelf: "flex-end",
        marginLeft: 'auto'
    },
    otherMessage: {
        backgroundColor: "#f0f0f0",
        color: "#333",
        alignSelf: "flex-start",
    },
};
