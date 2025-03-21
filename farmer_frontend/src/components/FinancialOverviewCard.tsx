import React, {useState} from "react";
import {Doughnut} from "react-chartjs-2";
import {Chart, ArcElement, Tooltip, Legend} from "chart.js";

Chart.register(ArcElement, Tooltip, Legend);

interface Transaction {
    icon: string;
    category: string;
    amount: number | string;
    unit?: string;
    description?: string;
}

interface FinancialOverviewProps {
    transactions: Transaction[];
    summaryData: {
        labels: string[];
        data: number[];
        colors: string[];
    };
}

const FinancialOverviewCard: React.FC<FinancialOverviewProps> = ({transactions, summaryData}) => {
    const [activeTab, setActiveTab] = useState<'Overview' | 'Cost Breakdown'>('Overview');

    const pieData = {
        labels: summaryData.labels,
        datasets: [{
            data: summaryData.data,
            backgroundColor: summaryData.colors
        }]
    };

    return (
        <div style={styles.card}>
            <div style={styles.tabContainer}>
                {['Overview', 'Cost Breakdown'].map(tab => (
                    <button
                        key={tab}
                        style={{...styles.tab, ...(activeTab === tab ? styles.activeTab : {})}}
                        onClick={() => setActiveTab(tab as 'Overview' | 'Cost Breakdown')}
                    >
                        {tab}
                    </button>
                ))}
            </div>

            {activeTab === 'Overview' && (
                <div style={styles.list}>
                    {transactions.map((tx, i) => (
                        <div key={i} style={styles.item}>
                            <div style={styles.left}>
                                <span>{tx.icon}</span>
                                <div style={styles.meta}>
                                    <span style={styles.category}>{tx.category}</span>
                                </div>
                            </div>
                            <div style={styles.right}>
                                <strong>{tx.amount}{tx.unit || ''}</strong>
                                {tx.description && <small style={styles.unit}>{tx.description}</small>}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {activeTab === 'Cost Breakdown' && (
                <div style={{ height: 359 }}>
                    <Doughnut
                        data={pieData}
                        options={{
                            maintainAspectRatio: false,
                            animation: false,
                            plugins: {
                                legend: {
                                    position: 'bottom',
                                    labels: {
                                        font: {
                                            family: 'Poppins',
                                            size: 16
                                        },
                                        generateLabels: (chart) => {
                                            const data = chart.data;
                                            const dataset = data.datasets?.[0];
                                            const values = dataset?.data as number[] | undefined;
                                            const backgroundColors = dataset?.backgroundColor as string[] | undefined;

                                            if (!data.labels || !values || !backgroundColors) return [];

                                            return data.labels.map((label, i) => ({
                                                text: `${label}: ₹${values[i].toLocaleString()}`,
                                                fillStyle: backgroundColors[i],
                                                strokeStyle: backgroundColors[i],
                                                fontFamily: 'Poppins',
                                                index: i
                                            }));
                                        }
                                    }
                                },
                                tooltip: { enabled: false }
                            }
                        }}
                    />
                </div>
            )}
        </div>
    );
};

export default FinancialOverviewCard;

const styles: { [key: string]: React.CSSProperties } = {
    card: {
        backgroundColor: '#fff',
        padding: 16,
        borderRadius: 12,
        boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
    },
    tabContainer: {display: 'flex', gap: 8, marginBottom: 12, fontFamily: 'Poppins'},
    tab: {
        flex: 1,
        padding: '10px 0',
        borderRadius: 9999,
        border: '1px solid #ccc',
        cursor: 'pointer',
        background: '#fff',
        fontWeight: 600,
        fontFamily: 'Poppins',
        fontSize: 18
    },
    activeTab: {
        backgroundColor: '#2e7d32',
        color: '#fff',
        border: '1px solid #2e7d32',
        fontFamily: 'Poppins',
    },
    list: {display: 'flex', flexDirection: 'column', gap: 12, fontFamily: 'Poppins'},
    item: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 0',
        borderBottom: '1px solid #eee',
        fontFamily: 'Poppins',
    },
    left: {display: 'flex', alignItems: 'center', gap: 12, fontFamily: 'Poppins'},
    meta: {display: 'flex', flexDirection: 'column', fontFamily: 'Poppins'},
    category: {
        fontWeight: 600, fontSize: 18, fontFamily: 'Poppins',
    },
    right: {textAlign: 'right', fontFamily: 'Poppins', fontSize: 18 },
    unit: {
        display: 'block', fontSize: 12, color: '#000',
        fontFamily: 'Poppins',
    },
};