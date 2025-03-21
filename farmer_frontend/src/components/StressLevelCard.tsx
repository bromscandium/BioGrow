import React from "react";
import { Bar } from "react-chartjs-2";
import { ChartOptions } from "chart.js";

interface StressLevelProps {
    data: {
        labels: string[];
        datasets: {
            label: string;
            data: number[];
            backgroundColor: string[];
            borderRadius: number;
        }[];
    };
    options: ChartOptions<'bar'>;
}

const StressLevelCard: React.FC<StressLevelProps> = ({ data, options }) => {
    return (
        <div style={styles.card}>
            <div style={styles.chartWrapper}>
                <Bar
                    data={data}
                    options={{
                        ...options,
                        plugins: {
                            ...options.plugins,
                            legend: { display: false },

                        },
                        interaction: { mode: undefined },
                        animation: false,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                ticks: {
                                    font: {
                                        family: 'Poppins',
                                        size: 16
                                    }
                                }
                            },
                            y: {
                                ticks: {
                                    font: {
                                        family: 'Poppins',
                                        size: 16
                                    }
                                }
                            }
                        }
                    }}
                />
            </div>
            <div style={styles.customLegend}>
                {data.labels.map((label, i) => (
                    <div key={i} style={styles.legendItem}>
                        <span style={{ ...styles.legendDot, backgroundColor: data.datasets[0].backgroundColor[i] }}></span>
                        <span style={styles.legendLabel}>{label}: {data.datasets[0].data[i]}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default StressLevelCard;

const styles: { [key: string]: React.CSSProperties } = {
    card: {
        backgroundColor: '#fff',
        padding: 16,
        borderRadius: 12,
        boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
        marginBottom: 16,
        fontFamily: 'Poppins',
    },
    chartWrapper: {
        height: 300,
    },
    customLegend: {
        marginTop: 12,
        display: 'flex',
        gap: 16,
        fontFamily: 'Poppins',
    },
    legendItem: {
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        fontFamily: 'Poppins',
    },
    legendDot: {
        width: 12,
        height: 12,
        borderRadius: '50%',
    },
    legendLabel: {
        fontSize: 16,
        color: '#000',
        fontFamily: 'Poppins'
    }
};
