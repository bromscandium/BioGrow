import React from "react";

interface RecommendationProps {
    header: { title: string; subtitle: string };
    description: string;
    benefits: string[];
    link: { text: string; url: string };
}

const RecommendationCard: React.FC<{ data: RecommendationProps }> = ({data}) => {
    return (
        <div style={styles.card}>
            <div style={styles.headerRow}>
                <div>
                    <h4 style={styles.title}>{data.header.title}</h4>
                    <p style={styles.subtitle}>{data.header.subtitle}</p>
                </div>
            </div>
            <p style={styles.description}>{data.description}</p>
            <p style={styles.benefitsTitle}>Benefits for your case</p>
            <ul>
                {data.benefits.map((item, idx) => (
                    <li key={idx} style={styles.benefitItem}>✅ {item}</li>
                ))}
            </ul>
            <a href={data.link.url} target="_blank" rel="noopener noreferrer" style={styles.link}>{data.link.text}</a>
        </div>
    );
};

export default RecommendationCard;

const styles: { [key: string]: React.CSSProperties } = {
    card: {
        backgroundColor: '#333',
        padding: 20,
        borderRadius: 16,
        color: '#fff',
        boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
    },
    header: {display: 'flex', alignItems: 'center', marginBottom: 12},
    title: {fontSize: 24, fontWeight: 700, fontFamily: 'Poppins'},
    subtitle: {fontSize: 20, fontWeight: 600, marginBottom: 8, fontFamily: 'Poppins',},
    description: {fontSize: 16, marginBottom: 12, color: '#ddd', fontFamily: 'Poppins',},
    benefitsTitle: {fontSize: 20, fontWeight: 600, marginBottom: 8, fontFamily: 'Poppins',},
    benefitList: {
        listStyle: 'none',
        padding: 0,
        margin: 0,
        display: 'flex',
        flexDirection: 'column',
        gap: 6,
        fontFamily: 'Poppins'
    },
    benefitItem: {
        fontSize: 18, fontFamily: 'Poppins'
    },
    link: {
        fontSize: 18,
        marginTop: 12,
        display: 'inline-block',
        color: '#4CAF50',
        fontWeight: 600,

        fontFamily: 'Poppins',
    }
};
