import React from "react";

interface InsightCardProps {
    title: string;
    description: string;
}

const InsightCard: React.FC<InsightCardProps> = ({title, description}) => {
    return (
        <div style={styles.card}>
            <div style={styles.row}>
                <h4 style={styles.title}>{title}</h4>
                <div style={styles.description}>{description}</div>
            </div>
        </div>
    );
};

export default InsightCard;

const styles: { [key: string]: React.CSSProperties } = {
    card: {
        backgroundColor: '#c8ffcb',
        paddingRight: 16,
        paddingLeft: 16,
        paddingBottom: 8,
        borderRadius: 12,
        boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)',
        marginBottom: 20,
    },
    title: {
        fontSize: '22px',
        fontWeight: 700,
        color: '#2e7d32',
        fontFamily: 'Poppins',
        margin: 0,
        paddingTop: 20,
        marginBottom: 10
    },
    row: {
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
    },
    description: {
        fontSize: '16px',
        color: '#555',
        fontFamily: 'Poppins',
        margin: 0,
        paddingBottom: 16
    },
};
