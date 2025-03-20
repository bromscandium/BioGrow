import React, {useState} from "react";

interface HealthCardProps {
    name: string;
    status: string;
    location: string;
    overall: number;
    frostRisk: string;
    waterNeeds: string;
    soilHealth: number;
    lastUpdated: Date;
    monitoringSince: Date;
}

const HealthCard: React.FC<HealthCardProps> = ({
                                                   name,
                                                   status,
                                                   location,
                                                   overall,
                                                   frostRisk,
                                                   waterNeeds,
                                                   soilHealth,
                                                   lastUpdated,
                                                   monitoringSince,
                                               }) => {
    const [isPrivate, setIsPrivate] = useState(true);

    const getBarColor = (value: number) => {
        if (value >= 80) return "#00A651";
        if (value >= 60) return "#FFC107";
        return "#FF3B30";
    };

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

    const daysSinceMonitoring = Math.floor(
        (new Date().getTime() - new Date(monitoringSince).getTime()) / (1000 * 60 * 60 * 24)
    );

    return (
        <div style={styles.card}>
            <div style={styles.headerRow}>
                <div style={styles.statusLocationWrapper}>
                    <span style={{...styles.statusBadge, backgroundColor: getStatusColor(status)}}>{status}</span>
                    <span style={styles.locationBadge}>{location}</span>
                </div>
                <div style={styles.actionsWrapper}>
                    <span style={{fontSize: 16, fontWeight: 600, color: isPrivate ? '#FF5252' : '#3F51B5'}}>
                        {isPrivate ? "Private" : "Public"}
                    </span>
                    <div
                        style={{...styles.toggleWrapper, backgroundColor: isPrivate ? '#FF5252' : '#3F51B5'}}
                        onClick={() => setIsPrivate(!isPrivate)}>
                        <div style={{
                            ...styles.toggleCircle,
                            marginLeft: isPrivate ? '23px' : '2px'
                        }}></div>
                    </div>
                    <button
                        onClick={() => alert("Shared!")}
                        style={{
                            background: 'none',
                            border: 'none',
                            padding: 0,
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center'
                        }}
                    >
                        <img src={"/assets/img.png"} alt="icon" style={{ width: 22, height: 22 }} />
                    </button>
                </div>
            </div>

            <h5 style={styles.cardTitle}>{name}</h5>

            <div style={styles.healthRow}>
                <span style={styles.sub}>Overall Health</span>
                <span style={styles.numberOverall}>{overall}%</span>
            </div>

            <div style={styles.barContainer}>
                <div style={{...styles.bar, width: `${overall}%`, backgroundColor: getBarColor(overall)}}/>
            </div>

            <div style={styles.statsContainer}>
                <div style={styles.metricBox}>
                    <span style={styles.metricLabel}>❄️ Frost Risk</span>
                    <span style={styles.metricValue}>{frostRisk}</span>
                </div>
                <div style={styles.metricBox}>
                    <span style={styles.metricLabel}>💧 Water Needs</span>
                    <span style={styles.metricValue}>{waterNeeds}</span>
                </div>
                <div style={styles.metricBox}>
                    <span style={styles.metricLabel}>🌱 Soil Health</span>
                    <span style={styles.metricValue}>{soilHealth}%</span>
                </div>
            </div>

            <div style={styles.dateContainer}>
                <div style={styles.dateBox}>
                    📅 Last Updated: <strong>{lastUpdated.toLocaleDateString()}</strong>
                </div>
                <div style={styles.dateBox}>
                    📌 Monitoring
                    Since: <strong>{monitoringSince.toLocaleDateString()} ({daysSinceMonitoring} days)</strong>
                </div>
            </div>
        </div>
    );
};

export default HealthCard;

const styles: { [key: string]: React.CSSProperties } = {
    card: {
        backgroundColor: '#fff',
        padding: 16,
        borderRadius: 12,
        boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)',
        marginBottom: 16,
    },
    headerRow: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    statusLocationWrapper: {
        display: 'flex',
        gap: 8,
        alignItems: 'center',
    },
    statusBadge: {
        fontSize: 14,
        color: '#fff',
        padding: '4px 8px',
        borderRadius: 9999,
        fontWeight: 600,
        textTransform: 'capitalize',
        minWidth: 80,
        textAlign: 'center',
    },
    locationBadge: {
        fontSize: 14,
        color: '#333',
        backgroundColor: '#f0f0f0',
        padding: '4px 8px',
        borderRadius: 9999,
        fontWeight: 500,
        minWidth: 80,
        textAlign: 'center',
    },
    actionsWrapper: {
        display: 'flex',
        alignItems: 'center',
        gap: 12,
    },
    toggleWrapper: {
        width: 50,
        height: 30,
        borderRadius: 9999,
        display: 'flex',
        alignItems: 'center',
        cursor: 'pointer',
        padding: 2,
        transition: 'background-color 0.3s ease',
        marginRight: 8,
    },
    toggleCircle: {
        width: 24,
        height: 24,
        backgroundColor: '#fff',
        borderRadius: '50%',
        transition: 'margin 0.3s ease',
    },
    shareButton: {
        fontSize: 20,
        padding: '4px 20px',
        border: '1px solid #ccc',
        borderRadius: 9999,
        background: '#fff',
        cursor: 'pointer',
        fontWeight: 500,
        transition: 'all 0.3s ease',
        display: 'flex',
        alignItems: 'center',
        gap: 4,
    },
    cardTitle: {
        fontSize: 24,
        fontWeight: 700,
        marginBottom: 6,
        fontFamily: 'Poppins, sans-serif',
    },
    healthRow: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 4,
    },
    numberOverall: {
        fontSize: 18,
        color: '#1F3A93',
        fontWeight: 700,
        fontFamily: 'Poppins, sans-serif',
    },
    barContainer: {
        width: '100%',
        height: 8,
        backgroundColor: '#E0E0E0',
        borderRadius: 4,
        overflow: 'hidden',
        marginBottom: 20,
    },
    bar: {
        height: '100%',
        borderRadius: 4,
        transition: 'width 0.3s ease',
    },
    statsContainer: {
        display: 'flex',
        gap: 8,
        marginBottom: 12,
    },
    metricBox: {
        flex: 1,
        padding: 8,
        backgroundColor: '#f0f0f0',
        borderRadius: 8,
        textAlign: 'center',
        fontFamily: 'Poppins, sans-serif',
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
    },
    metricLabel: {
        fontSize: 14,
        color: '#555',
        fontWeight: 500,
    },
    metricValue: {
        fontSize: 18,
        fontWeight: 600,
        color: '#1F3A93',
    },
    dateContainer: {
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
    },
    dateBox: {
        backgroundColor: '#f0f0f0',
        padding: 8,
        borderRadius: 8,
        fontSize: 15,
        fontFamily: 'Poppins, sans-serif',
    },
    sub: {
        fontSize: 16,
        color: '#666',
        fontFamily: 'Poppins, sans-serif',
    },
};