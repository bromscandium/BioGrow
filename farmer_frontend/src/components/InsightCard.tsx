import React from "react";

interface InsightCardProps {
    icon: string;
    title: string;
    description: string;
}

const InsightCard: React.FC<InsightCardProps> = ({icon, title, description}) => {
    return (
        <div style={styles.card}>
            <div style={styles.row}>
                <span style={styles.icon}>{icon}</span>
                <h4 style={styles.title}>{title}</h4>
            </div>
            <p style={styles.description}>{description}</p>
        </div>
    );
};

export default InsightCard;

const styles: { [key: string]: React.CSSProperties } = {
    card: {
        backgroundColor: '#c8ffcb',
        padding: 16,
        borderRadius: 12,
        boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)',
        marginBottom: 16,
    },
    row: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginBottom: '4px',
    },
    icon: {
        fontSize: '18px',
    },
    title: {
        fontSize: '16px',
        fontWeight: 700,
        color: '#2e7d32',
        fontFamily: 'Poppins'
    },
    description: {
        fontSize: '14px',
        color: '#555',
        fontFamily: 'Poppins'
    }
};
