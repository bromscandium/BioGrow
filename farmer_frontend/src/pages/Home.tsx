import React, { useState } from "react";
import BottomNav from "../components/BottomNav";
import Header from "../components/Header";
import { styles } from "../styles/Home.styles";

const HomeScreen: React.FC = () => {
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
        if (hour < 6) return "Good night,";
        if (hour < 12) return "Good morning,";
        if (hour < 18) return "Good afternoon,";
        return "Good evening,";
    };

    const getBarColor = (value: string) => {
        const num = parseInt(value, 10);
        if (num >= 80) return "#00A651";
        if (num >= 60) return "#FFC107";
        return "#FF3B30";
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "Good": return "#00A651";
            case "Moderate": return "#FFC107";
            case "Needs Attention": return "#FF3B30";
            default: return "#888";
        }
    };

    return (
        <div className={styles.container}>
            <Header />
            <div className={styles.scrollContent}>
                {/* Hello Info */}
                <div className={styles.helloContainer}>
                    <div>
                        <p className={styles.greeting}>{getGreeting()}</p>
                        <h2 className={styles.username}>{userInfo.name}</h2>
                    </div>
                    <p className={styles.temp}>{Weather.temp}</p>
                </div>

                {/* User Info */}
                <div className={styles.card}>
                    <h3 className={styles.name}>{userInfo.name}</h3>
                    <p className={styles.sub}>Rank: {userInfo.rank} • {userInfo.points} pts</p>
                    <p className={styles.sub}>{userInfo.location}</p>
                </div>

                {/* Projects */}
                <section className={styles.section}>
                    <h4 className={styles.sectionTitle}>Your Projects</h4>
                    {Projects.map((project) => (
                        <div key={project.id} className={styles.card}>
                            <div className={styles.badgeRow}>
                                <span className={styles.statusBadge} style={{ backgroundColor: getStatusColor(project.status) }}>
                                    {project.status}
                                </span>
                            </div>
                            <h5 className={styles.cardTitle}>{project.name}</h5>
                            <p className={styles.date}>Last Updated: {new Date(project.lastUpdated).toLocaleDateString()}</p>
                            <div className={styles.healthRow}>
                                <p className={styles.sub}>Health</p>
                                <p className={styles.numberOverall}>{project.overall}</p>
                            </div>
                            <div className={styles.barContainer}>
                                <div className={styles.bar} style={{ width: `${project.overall}%`, backgroundColor: getBarColor(project.overall) }} />
                            </div>
                            <div className={styles.statsRow}>
                                <p className={styles.sub}>Water Needs: {project.waterNeeds}</p>
                                <p className={styles.sub}>Soil Health: {project.soilHealth}%</p>
                            </div>
                            <p className={styles.viewButton}>View Details ➜</p>
                        </div>
                    ))}
                </section>

                {/* Weather Section */}
                <section className={styles.section}>
                    <div className={styles.weatherHeader}>
                        <h4 className={styles.sectionTitle}>Weather Insights</h4>
                        <span className={styles.badge}>{Weather.humidity}</span>
                    </div>
                    <div className={styles.weatherCard}>
                        <div className={styles.weatherMain}>
                            <div>
                                <h3 className={styles.weatherTemp}>{Weather.temp}</h3>
                                <p className={styles.weatherSub}>Feels like 31°C</p>
                            </div>
                            <div className={styles.weatherRight}>
                                <p className={styles.weatherDetail}>High: 32°C</p>
                                <p className={styles.weatherDetail}>Low: 24°C</p>
                                <p className={styles.weatherDetail}>💧 65% humidity</p>
                            </div>
                        </div>
                        <div className={styles.weatherFooter}>
                            <p>🌤 Partly Cloudy</p>
                            <p>🌧 10% chance of rain</p>
                        </div>
                        <div className={styles.tip}>
                            <p className={styles.tipText}>{Weather.tip}</p>
                        </div>
                    </div>
                </section>

                {/* Community Updates */}
                <section className={styles.section}>
                    <h4 className={styles.sectionTitle}>Community Updates</h4>
                    {Community.map(update => (
                        <div key={update.id} className={styles.card}>
                            <h5 className={styles.cardTitle}>{update.headline}</h5>
                            <p>{update.summary}</p>
                            <p className={styles.date}>{update.date}</p>
                        </div>
                    ))}
                </section>
            </div>
            <BottomNav />
        </div>
    );
};

export default HomeScreen;
