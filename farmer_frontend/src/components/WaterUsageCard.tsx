import React, {useState} from "react";
import {Doughnut, Bar} from 'react-chartjs-2';
import {Chart, ArcElement, CategoryScale, LinearScale, BarElement, Tooltip, Legend} from 'chart.js';

Chart.register(ArcElement, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

interface WaterOverviewProps {
    waterSources: {
        labels: string[];
        data: number[];
        colors: string[];
    };
    waterUsage: {
        labels: string[];
        current: number[];
        estimated: number[];
        colors: {
            current: string;
            estimated: string;
        };
    };
}

const WaterUsageCard: React.FC<WaterOverviewProps> = ({waterSources, waterUsage}) => {
    const [activeTab, setActiveTab] = useState<'Sources' | 'Usage'>('Sources');

    const pieData = {
        labels: waterSources.labels,
        datasets: [
            {
                data: waterSources.data,
                backgroundColor: waterSources.colors,
            }
        ]
    };

    const barData = {
        labels: waterUsage.labels,
        datasets: [
            {
                label: 'Current',
                data: waterUsage.current,
                backgroundColor: waterUsage.colors.current,
                borderRadius: 12,
            },
            {
                label: 'Estimated',
                data: waterUsage.estimated,
                backgroundColor: waterUsage.colors.estimated,
                borderRadius: 12,
            }
        ]
    };

    return (
        <div style={styles.card}>
            <div style={styles.tabContainer}>
                {['Sources', 'Usage'].map((tab) => (
                    <button
                        key={tab}
                        style={{...styles.tab, ...(activeTab === tab ? styles.activeTab : {})}}
                        onClick={() => setActiveTab(tab as 'Sources' | 'Usage')}
                    >
                        {tab}
                    </button>
                ))}
            </div>
            <div style={styles.chartContainer}>
                {activeTab === 'Sources' && (
                    <Doughnut
                        data={pieData}
                        options={{
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: 'bottom',
                                    labels: {
                                        generateLabels: (chart) => {
                                            const dataset = chart.data.datasets[0];
                                            const bg = dataset.backgroundColor as string[];
                                            return chart.data.labels?.map((label, i) => ({
                                                text: `${label}: ${dataset.data[i]} m³`,
                                                fillStyle: bg[i],
                                                strokeStyle: bg[i],
                                                index: i
                                            })) || [];
                                        }
                                    }
                                },
                                tooltip: {enabled: false}
                            }
                        }}
                    />
                )}

                {activeTab === 'Usage' && (
                    <Bar
                        data={barData}
                        options={{
                            responsive: true,
                            plugins: {
                                legend: {position: 'bottom'}
                            }
                        }}
                    />
                )}
            </div>
        </div>
    );
};

export default WaterUsageCard;

const styles: { [key: string]: React.CSSProperties } = {
    card: {
        backgroundColor: '#fff',
        padding: 16,
        borderRadius: 12,
        boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
    },
    chartHeader: {
        fontSize: 18,
        fontWeight: 700,
        fontFamily: 'Poppins',
        marginBottom: 12,
        color: '#000',
    },
    tabContainer: {
        display: 'flex',
        marginBottom: 12,
        gap: 8,
    },
    tab: {
        flex: 1,
        padding: '8px 0',
        borderRadius: 9999,
        border: '1px solid #ccc',
        cursor: 'pointer',
        backgroundColor: '#fff',
        fontWeight: 600,
        fontFamily: 'Poppins',
        fontSize: 15,
        transition: 'all 0.3s ease',
        color: '#000',
    },
    activeTab: {
        backgroundColor: '#2e7d32',
        color: '#fff',
        border: '1px solid #2e7d32',
        fontFamily: 'Poppins',
    },
    chartContainer: {
        padding: '12px',
    },
};
