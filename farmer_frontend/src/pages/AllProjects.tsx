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
            location: "New Delhi",
            frostRisk: "Low",
            waterNeeds: "Medium",
            soilHealth: 80,
            lastUpdated: new Date(),
            newInsights: 3,
        },
        {
            id: 2,
            name: "Corn Farm",
            status: "Needs Attention",
            location: "Mumbai",
            frostRisk: "High",
            waterNeeds: "High",
            soilHealth: 65,
            lastUpdated: new Date(),
            newInsights: 1,
        },
        {
            id: 3,
            name: "Rice Paddies",
            status: "Moderate",
            location: "Hyderabad",
            frostRisk: "Moderate",
            waterNeeds: "Medium",
            soilHealth: 72,
            lastUpdated: new Date(),
            newInsights: 0,
        },
        {
            id: 4,
            name: "Wheat Paddies",
            status: "Moderate",
            location: "Chennai",
            frostRisk: "Low",
            waterNeeds: "High",
            soilHealth: 40,
            lastUpdated: new Date(),
            newInsights: 5,
        },
    ];

    return (
        <div style={styles.container}>
            <Header/>
            <div style={styles.scrollContainer}>
                <h2 style={styles.title}>All Projects</h2>
                {Projects.map(project => (
                    <ProjectCard
                        key={project.id}
                        {...project}
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
        fontSize: '28px',
        fontWeight: 700,
        marginBottom: '16px',
        fontFamily: 'Poppins, sans-serif',
    }
};
