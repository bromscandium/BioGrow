import React from "react";
import ProjectCard from "../components/ProjectCard";
import BottomNav from "../components/BottomNav";
import Header from "../components/Header";

const AllProjects: React.FC = () => {
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
        {
            id: 4,
            name: "Wheat Paddies",
            status: "Moderate",
            waterNeeds: "High",
            soilHealth: 40,
            overall: "88",
            lastUpdated: Date.now()
        },
    ];

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
            <div style={styles.scrollContainer}>
                <h2 style={styles.title}>All Projects</h2>
                {Projects.map(project => (
                    <ProjectCard
                        key={project.id}
                        {...project}
                        getStatusColor={getStatusColor}
                        getBarColor={getBarColor}
                    />
                ))}
            </div>
            <BottomNav/>
        </div>
    );
};

export default AllProjects;

const styles: { [key: string]: React.CSSProperties } = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5',
    },
    scrollContainer: {
        padding: '16px',
        paddingBottom: '96px',
        flex: 1,
        overflowY: 'auto',
    },
    title: {
        fontSize: '22px',
        fontWeight: 700,
        marginBottom: '16px',
        fontFamily: 'Poppins, sans-serif',
    }
};
