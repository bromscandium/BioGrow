import React, {useState} from "react";
import {Link} from 'react-router-dom';
import Header from "../components/Header";
import BottomNav from "../components/BottomNav";

const Home: React.FC = () => {
    const [userInfo] = useState({
        name: "Arjun",
        rank: "Gold",
        points: 1200,
        location: "New Delhi",
    });

    const Projects = [
        {
            id: 1,
            name: "Wheat Field",
            status: "Good",
            waterNeeds: "Medium",
            soilHealth: 80,
            overall: "92",
            lastUpdated: Date.now()
        },
        {
            id: 2,
            name: "Corn Farm",
            status: "Needs Attention",
            waterNeeds: "High",
            soilHealth: 65,
            overall: "68",
            lastUpdated: Date.now()
        },
        {
            id: 3,
            name: "Rice Paddies",
            status: "Moderate",
            waterNeeds: "Medium",
            soilHealth: 72,
            overall: "80",
            lastUpdated: Date.now()
        },
    ];
    const Weather = {
        temp: "29°C",
        rain: "10%",
        condition: "Sunny",
        humidity: "Partly Cloudy",
        tip: "Farming Tip: Ideal conditions for crop monitoring today. Check moisture levels in the afternoon."
    };
    const Community = [
        {
            id: 1,
            headline: "New pest control methods",
            summary: "Farmers discuss new eco-friendly solutions.",
            date: "2025-03-19"
        },
        {
            id: 2,
            headline: "Soil health webinar",
            summary: "Upcoming event about soil sustainability.",
            date: "2025-03-18"
        },
        {
            id: 3,
            headline: "Water conservation tips",
            summary: "Best practices from leading experts.",
            date: "2025-03-17"
        },
    ];

    const getGreeting = () => {
        const hour = new Date().getHours();
        if (hour < 6) return "🌙 Good night,";
        if (hour < 12) return "☀️ Good morning,";
        if (hour < 18) return "🌤️️ Good afternoon,";
        return "🌕 Good evening,";
    };

    const getBarColor = (value: string) => {
        const num = parseInt(value, 10);
        if (num >= 80) return "#00A651";
        if (num >= 60) return "#FFC107";
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

    return (
        <div style={styles.container}>
            <Header/>
            <div style={styles.scrollContent}>
                {/* Hello Info */}
                <div style={styles.helloContainer}>
                    <div>
                        <p style={{...styles.greeting, marginTop: '8px'}}>{getGreeting()}</p>
                        <h2 style={{...styles.username, marginTop: '-4px', marginBottom: '-4px'}}>{userInfo.name}</h2>
                    </div>
                </div>

                {/* User Info */}
                <div style={styles.card}>
                    <h3 style={styles.name}>{userInfo.name}</h3>
                    <p style={styles.sub}>Rank: {userInfo.rank} • {userInfo.points} pts</p>
                    <p style={styles.sub}>{userInfo.location}</p>
                </div>

                {/* Projects */}
                <section style={styles.section}>
                    <h4 style={styles.sectionTitle}>Your Projects</h4>
                    {Projects.map((project) => (
                        <Link
                            key={project.id}
                            to={`/projects/${project.id}`}
                            style={{textDecoration: 'none', color: 'inherit'}}
                        >
                            <div style={styles.card}>
                                <div style={styles.badgeRow}>
                <span style={{...styles.statusBadge, backgroundColor: getStatusColor(project.status)}}>
                    {project.status}
                                </span>
                                </div>
                                <h5 style={styles.cardTitle}>{project.name}</h5>
                                <p style={styles.date}>Last
                                    Updated: {new Date(project.lastUpdated).toLocaleDateString()}</p>
                                <div style={styles.healthRow}>
                                    <p style={styles.sub}>Health</p>
                                    <p style={styles.numberOverall}>{project.overall}</p>
                                </div>
                                <div style={styles.barContainer}>
                                    <div style={{
                                        ...styles.bar,
                                        width: `${project.overall}%`,
                                        backgroundColor: getBarColor(project.overall)
                                    }}/>
                                </div>
                                <div style={styles.statsRow}>
                                    <p style={styles.sub}>💧 Water Needs: {project.waterNeeds}</p>
                                    <p style={styles.sub}>🌱 Soil Health: {project.soilHealth}%</p>
                                </div>
                                <p style={styles.viewButton}>View Details ➜</p>
                            </div>
                        </Link>
                    ))}
                </section>

                {/* Weather Section */}
                <section style={styles.section}>
                    <div style={styles.weatherHeader}>
                        <h4 style={styles.sectionTitle}>Weather Insights</h4>
                        <span style={styles.badge}>{Weather.humidity}</span>
                    </div>
                    <div style={styles.weatherCard}>
                        <div style={styles.weatherMain}>
                            <div>
                                <h3 style={styles.weatherTemp}>{Weather.temp}</h3>
                                <p style={styles.weatherSub}>Feels like 31°C</p>
                            </div>
                            <div style={styles.weatherRight}>
                                <p style={styles.weatherDetail}>High: 32°C</p>
                                <p style={styles.weatherDetail}>Low: 24°C</p>
                                <p style={styles.weatherDetail}>💧 65% humidity</p>
                            </div>
                        </div>
                        <div style={styles.weatherFooter}>
                            <p>🌤 Partly Cloudy</p>
                            <p>🌧 10% chance of rain</p>
                        </div>
                        <div style={styles.tip}>
                            <p style={styles.tipText}>💡{Weather.tip}</p>
                        </div>
                    </div>
                </section>

                {/* Community Updates */}
                <section style={styles.section}>
                    <h4 style={styles.sectionTitle}>Community Updates</h4>
                    {Community.map(update => (
                        <div key={update.id} style={styles.card}>
                            <h5 style={styles.cardTitle}>{update.headline}</h5>
                            <p>{update.summary}</p>
                            <p style={styles.date}>{update.date}</p>
                        </div>
                    ))}
                </section>
            </div>
            <BottomNav/>
        </div>
    );
};

export default Home;

const styles: { [key: string]: React.CSSProperties } = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5',
    },
    scrollContent: {
        padding: '16px',
        paddingBottom: '96px',
    },
    helloContainer: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
    },
    greeting: {
        fontSize: '14px',
        color: '#666',
        marginBottom: '4px',
        fontFamily: 'Poppins, sans-serif',
    },
    username: {
        fontSize: '24px',
        fontWeight: 700,
        color: '#000',
        fontFamily: 'Poppins, sans-serif',
    },
    temp: {
        fontSize: '16px',
        color: '#000',
    },
    card: {
        backgroundColor: '#fff',
        padding: '16px',
        borderRadius: '12px',
        boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)',
        marginBottom: '16px',
    },
    name: {
        fontSize: '20px',
        fontWeight: 700,
        color: '#000',
        fontFamily: 'Poppins, sans-serif',
    },
    sub: {
        fontSize: '14px',
        color: '#666',
        fontFamily: 'Poppins, sans-serif',
    },
    section: {
        marginBottom: '24px',
    },
    sectionTitle: {
        fontSize: '18px',
        marginBottom: '12px',
        fontFamily: 'Poppins, sans-serif',
    },
    badgeRow: {
        display: 'flex',
        justifyContent: 'flex-start',
        alignItems: 'center',
        marginBottom: '8px',
    },
    statusBadge: {
        fontSize: '12px',
        color: '#fff',
        padding: '4px 8px',
        borderRadius: '9999px',
        fontFamily: 'Poppins, sans-serif',
    },
    cardTitle: {
        fontSize: '16px',
        fontWeight: 700,
        marginBottom: '4px',
        fontFamily: 'Poppins, sans-serif',
    },
    date: {
        fontSize: '12px',
        color: '#999',
        fontFamily: 'Poppins, sans-serif',
    },
    healthRow: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '4px',
    },
    numberOverall: {
        fontSize: '18px',
        color: '#1F3A93',
        fontWeight: 700,
        fontFamily: 'Poppins, sans-serif',
    },
    barContainer: {
        width: '100%',
        height: '8px',
        backgroundColor: '#E0E0E0',
        borderRadius: '4px',
        overflow: 'hidden',
        marginBottom: '8px',
    },
    bar: {
        height: '100%',
        borderRadius: '4px',
        transition: 'all 0.3s ease',
    },
    statsRow: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: '8px',
    },
    viewButton: {
        marginTop: '8px',
        color: '#1F3A93',
        fontWeight: 600,
        textAlign: 'right',
        cursor: 'pointer',
        fontFamily: 'Poppins, sans-serif',
    },
    // Weather Section
    weatherHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px',
    },
    badge: {
        backgroundColor: '#eee',
        padding: '4px 12px',
        borderRadius: '9999px',
        fontSize: '12px',
        color: '#555',
        fontFamily: 'Poppins, sans-serif',
    },
    weatherCard: {
        padding: '16px',
        backgroundColor: '#fff',
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
    },
    weatherMain: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    weatherTemp: {
        fontSize: '24px',
        fontWeight: 700,
        fontFamily: 'Poppins, sans-serif',
    },
    weatherSub: {
        fontSize: '12px',
        color: '#555',
        fontFamily: 'Poppins, sans-serif',
    },
    weatherRight: {
        textAlign: 'right',
    },
    weatherDetail: {
        fontSize: '12px',
        color: '#555',
        fontFamily: 'Poppins, sans-serif',
    },
    weatherFooter: {
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '14px',
    },
    tip: {
        backgroundColor: '#E5EFFF',
        padding: '8px',
        borderRadius: '8px',
        marginTop: '8px',
    },
    tipText: {
        fontSize: '12px',
        color: '#1F3A93',
        fontFamily: 'Poppins, sans-serif',
    },
};
