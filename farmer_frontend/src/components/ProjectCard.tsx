import React from "react";

interface ProjectCardProps {
    name: string;
    status: string;
    location: string;
    waterNeeds: string;
    soilHealth: number;
    frostRisk: string;
    lastUpdated: Date;
    newInsights: number;
}

const ProjectCard: React.FC<ProjectCardProps> = ({
                                                     name,
                                                     status,
                                                     location,
                                                     waterNeeds,
                                                     soilHealth,
                                                     frostRisk,
                                                     lastUpdated,
                                                     newInsights,
                                                 }) => {
    const getStatusColor = (status: string) => {
        switch (status) {
            case "Good":
                return "#00A651";
            case "Moderate":
                return "#FFC107";
            case "Needs Attention":
                return "#FF3B30";
            default:
                return "#888";
        }
    };

    return (
        <div style={styles.card}>
            <div style={styles.inlineBadgesRow}>
                <span style={{...styles.statusBadge, backgroundColor: getStatusColor(status)}}>{status}</span>
                <span style={styles.locationBadge}>📍{location}</span>
                <span style={styles.insightsBadge}>{newInsights} new insights</span>
            </div>

            <h5 style={styles.cardTitle}>{name}</h5>

            <div style={styles.statsContainer}>
                <div style={styles.metricBox}>
                    <span style={styles.metricLabel}>Frost Risk</span>
                    <span style={styles.metricValue}>{frostRisk}</span>
                </div>
                <div style={styles.metricBox}>
                    <span style={styles.metricLabel}>Water Needs</span>
                    <span style={styles.metricValue}>{waterNeeds}</span>
                </div>
                <div style={styles.metricBox}>
                    <span style={styles.metricLabel}>Soil Health</span>
                    <span style={styles.metricValue}>{soilHealth}%</span>
                </div>
            </div>

            <div style={styles.footerRow}>
                <span style={styles.lastUpdated}>Last Updated: {lastUpdated.toLocaleDateString()}</span>
            </div>
        </div>
    );
};

export default ProjectCard;

const styles: { [key: string]: React.CSSProperties } = {
    card: {
        backgroundColor: '#fff',
        padding: 16,
        borderRadius: 12,
        boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)',
        marginBottom: 16,
        fontFamily: 'Poppins, sans-serif',
    },
    inlineBadgesRow: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    cardTitle: {
        fontSize: 24,
        fontWeight: 700,
        fontFamily: 'Poppins, sans-serif',
        marginBottom: 12,
    },
    locationBadge: {
        fontSize: 18,
        color: '#333',
        padding: '8px 0px',
        borderRadius: 9999,
        fontWeight: 500,
        minWidth: 80,
        textAlign: 'center',
    },
    statusBadge: {
        fontSize: 18,
        color: '#fff',
        padding: '8px 12px',
        borderRadius: 9999,
        fontWeight: 600,
        textTransform: 'capitalize',
        minWidth: 80,
        textAlign: 'center',
    },
    insightsBadge: {
        fontSize: 18,
        color: '#fff',
        backgroundColor: '1F3A93',
        padding: '8px 12px',
        borderRadius: 9999,
        fontWeight: 600,
        textTransform: 'capitalize',
        minWidth: 80,
        textAlign: 'center',
    },
    statsContainer: {
        display: 'flex',
        gap: 14,
        marginBottom: 14,
    },
    metricBox: {
        padding: 14,
        flex: 1,
        backgroundColor: '#f0f0f0',
        borderRadius: 8,
        textAlign: 'center',
        fontFamily: 'Poppins, sans-serif',
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
    },
    metricLabel: {
        fontSize: 16,
        color: '#555',
        fontWeight: 500,
    },
    metricValue: {
        fontSize: 20,
        fontWeight: 600,
        color: '#1F3A93',
    },
    footerRow: {
        marginTop: 12,
    },
    lastUpdated: {
        marginTop: 12,
        fontSize: 18,
        color: '#888',
        fontFamily: 'Poppins, sans-serif',
    },
};