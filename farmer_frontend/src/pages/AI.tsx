import React, {useState, useEffect} from "react";
import Header from "../components/Header";
import BottomNav from "../components/BottomNav";

const AI = () => {
    const [input, setInput] = useState("");
    const [bottomOffset, setBottomOffset] = useState(64);
    const [messages, setMessages] = useState([
        { text: "Hello!", sender: "You" },
        { text: "Hi there!", sender: "Other User" }
    ]);

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

    const handleSend = () => {
        if (input.trim() === "") return;
        console.log("Send message:", input);
        setMessages([...messages, { text: input, sender: "You" }]);
        setInput("");
    };


    const handleVoice = () => {
        console.log("Voice input triggered");
    };

    return (
        <div style={styles.container}>
            <Header/>
            <div style={styles.chatArea}></div>
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
                        <div style={styles.messageSender}>{message.sender}</div>
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
        fontSize: "14px",
        color: "#333",
        lineHeight: "1.4",
    },
    messageSender: {
        fontSize: "12px",
        color: "#888",
        textAlign: "right",
        marginTop: "4px",
    },
    userMessage: {
        backgroundColor: "#1F3A93",
        color: "#fff",
        alignSelf: "flex-end",
    },
    otherMessage: {
        backgroundColor: "#f0f0f0",
        color: "#333",
        alignSelf: "flex-start",
    },
};
