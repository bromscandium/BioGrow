import React, {useState} from "react";
import Header from "../components/Header";
import BottomNav from "../components/BottomNav";
import {Bar} from 'react-chartjs-2';
import {Chart, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend} from 'chart.js';
import HealthCard from "../components/HealthCard";
import InsightCard from "../components/InsightCard";
import WaterUsageCard from "../components/WaterUsageCard";

Chart.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Project = () => {
    const [activeInsight, setActiveInsight] = useState('Environment');

    const tabs = ['Environment', 'Business', 'Protection'];

    const environmentInsights = [
        {
            icon: "🌿",
            title: "Growth Efficiency",
            description: "Your crop is growing 15% faster than regional average for this time of year."
        },
        {
            icon: "💧",
            title: "Water Efficiency",
            description: "You're using 20% less water than last season while maintaining excellent crop health."
        },
        {
            icon: "🌧️",
            title: "Rainfall Utilization",
            description: "Based on current growth rate, optimal harvest time will be November 25-30."
        },
    ];

    const businessInsights = [
        {
            icon: "📈",
            title: "Market Trends",
            description: "Market prices for Cotton are projected to rise 8% by harvest time."
        },
        {
            icon: "💹",
            title: "Cost Efficiency",
            description: "Your operational costs are 10% lower than regional competitors."
        },
    ];

    const protectionInsights = [
        {icon: "🦠", title: "Pest Risk", description: "Slightly increased risk of aphids due to mild weather."},
        {icon: "🛡️", title: "Crop Shield", description: "Biological protection recommended for next week."},
    ];

    const getCurrentInsights = () => {
        if (activeInsight === 'Environment') return environmentInsights;
        if (activeInsight === 'Business') return businessInsights;
        if (activeInsight === 'Protection') return protectionInsights;
        return [];
    };

    const dataStress = {
        labels: ['Daytime', 'Nighttime'],
        datasets: [
            {
                label: 'Heat Stress Levels',
                data: [3, 7],
                backgroundColor: ['#FFC107', '#1F3A93'],
                borderRadius: 12,
            },
        ],
    };

    const optionsStress = {
        responsive: true,
    };

    const waterData = {
        waterSources: {
            labels: ['Tube Wells', 'Canal', 'Sprinkler', 'Drip'],
            data: [52, 22.8, 13.9, 11.3],
            colors: ['#4CAF50', '#2196F3', '#FFC107', '#FF5722']
        },
        waterUsage: {
            labels: ['January', 'February', 'March', 'April'],
            current: [22000, 20000, 25000, 21000],
            estimated: [15000, 17000, 19000, 18000],
            colors: {
                current: '#1F3A93',
                estimated: '#FFC107'
            }
        }
    };

    return (
        <div style={styles.container}>
            <Header/>

            <div style={styles.scrollContainer}>
                {/*Health card*/}
                <section style={styles.section}>
                    <HealthCard
                        name="Wheat Field"
                        status="Good"
                        location="New Delhi"
                        overall={92}
                        frostRisk="Low"
                        waterNeeds="High"
                        soilHealth={88}
                        lastUpdated={new Date("2025-03-20")}
                        monitoringSince={new Date("2025-01-10")}
                    />
                </section>

                {/*Your insights*/}
                <section style={styles.section}>
                    <h3 style={styles.sectionTitle}>Your Daily Insights</h3>
                    <div style={styles.tabContainer}>
                        {tabs.map(tab => (
                            <button
                                key={tab}
                                style={{...styles.tab, ...(activeInsight === tab ? styles.activeTab : {})}}
                                onClick={() => setActiveInsight(tab)}
                            >
                                {tab}
                            </button>
                        ))}
                    </div>
                    <div>
                        {getCurrentInsights().map((item, idx) => (
                            <InsightCard key={idx} {...item} />
                        ))}
                    </div>
                </section>

                {/*Stress level*/}
                <section style={styles.section}>
                    <h3 style={styles.sectionTitle}>Heat Stress Levels</h3>
                    <Bar data={dataStress} options={optionsStress}/>;
                </section>

                {/*Water usage*/}
                <section style={styles.section}>
                    <h3 style={styles.sectionTitle}>Water Usage</h3>
                    <WaterUsageCard
                        waterSources={waterData.waterSources}
                        waterUsage={waterData.waterUsage}
                    />
                </section>

                {/*Financial overview*/}
                <section style={styles.section}>
                    <h3 style={styles.sectionTitle}>Financial Overview</h3>
                    <div style={styles.financialCard}><span>💰 Estimated Profit</span><strong>₹15,000/acre</strong></div>
                    <div style={styles.financialCard}><span>🌾 Yield Expectation</span><strong>1,800kg/acre</strong>
                    </div>
                </section>

                {/*Biological Product Recommendations*/}
                <section style={styles.section}>
                    <h3 style={styles.sectionTitle}>Biological Product Recommendations</h3>
                    <div style={styles.card}>🛠️ Stress Buster: Helps resist heat & drought.</div>
                </section>

            </div>

            <BottomNav/>
        </div>
    );
};

export default Project;


const styles: { [key: string]: React.CSSProperties } = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5',
    },
    scrollContainer: {
        padding: '16px 16px 96px 16px',
        overflowY: 'auto',
        flex: 1,
    },
    section: {marginBottom: '20px'},
    sectionTitle: {fontSize: '22px', marginBottom: '12px', color: '#000', fontWeight: 600, fontFamily: 'Poppins'},
    tabContainer: {display: 'flex', gap: '8px', marginBottom: '12px'},
    tab: {
        flex: 1,
        textAlign: 'center',
        padding: '10px 0',
        borderRadius: '999px',
        border: '1px solid #ccc',
        cursor: 'pointer',
        backgroundColor: '#fff',
        fontWeight: 600,
        fontSize: '15px',
        transition: 'all 0.3s ease',
        fontFamily: 'Poppins',
        color: '#000',
    },
    activeTab: {
        backgroundColor: "#2e7d32",
        color: '#fff',
        border: '1px solid #2e7d32',
        fontFamily: 'Poppins'
    },
    projectCard: {
        backgroundColor: '#fff',
        padding: '14px',
        borderRadius: '12px',
        marginBottom: '12px',
        boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
    },
    row: {display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px'},
    icon: {fontSize: '20px'},
    title: {fontSize: '18px', fontWeight: 700, color: '#000', fontFamily: 'Poppins'},
    description: {fontSize: '14px', color: '#333', fontFamily: 'Poppins'}
};