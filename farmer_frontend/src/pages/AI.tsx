import React, { useState } from "react";
import Header from "../components/Header";
import BottomNav from "../components/BottomNav";

const AI = () => {
    const [messages, setMessages] = useState([
        { id: 1, sender: "bot", text: "Hello! How can I assist you today?" }
    ]);
    const [input, setInput] = useState("");

    const handleSend = () => {
        if (input.trim() === "") return;
        setMessages([...messages, { id: Date.now(), sender: "user", text: input }]);
        setInput("");
    };

    return (
        <div style={styles.container}>
            <Header />
            <div style={styles.chatContainer}>
                <div style={styles.messages}>
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            style={{
                                ...styles.message,
                                alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                                backgroundColor: msg.sender === "user" ? "#1F3A93" : "#E5E5EA",
                                color: msg.sender === "user" ? "#fff" : "#000",
                            }}
                        >
                            {msg.text}
                        </div>
                    ))}
                </div>
                <div style={styles.inputContainer}>
                    <input
                        style={styles.input}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                    />
                    <button style={styles.button} onClick={handleSend}>Send</button>
                </div>
            </div>
            <BottomNav />
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
    },
    chatContainer: {
        flex: 1,
        display: "flex",
        flexDirection: "column",
        padding: "16px",
        paddingBottom: "80px",
    },
    messages: {
        flex: 1,
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        overflowY: "auto",
        marginBottom: "16px",
    },
    message: {
        maxWidth: "70%",
        padding: "10px 14px",
        borderRadius: "16px",
        fontFamily: "Poppins, sans-serif",
        fontSize: "14px",
    },
    inputContainer: {
        display: "flex",
        gap: "8px",
    },
    input: {
        flex: 1,
        padding: "12px",
        borderRadius: "9999px",
        border: "1px solid #ccc",
        fontFamily: "Poppins, sans-serif",
        fontSize: "14px",
    },
    button: {
        padding: "12px 20px",
        backgroundColor: "#1F3A93",
        color: "#fff",
        border: "none",
        borderRadius: "9999px",
        cursor: "pointer",
        fontFamily: "Poppins, sans-serif",
    },
};
