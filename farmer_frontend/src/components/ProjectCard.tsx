import React from "react";
import {Link} from "react-router-dom";

interface ProjectProps {
    id: number;
    name: string;
    status: string;
    waterNeeds: string;
    soilHealth: number;
    overall: string;
    lastUpdated: number;
    getStatusColor: (status: string) => string;
    getBarColor: (value: string) => string;
}

const ProjectCard: React.FC<ProjectProps> = ({
                                                 id,
                                                 name,
                                                 status,
                                                 waterNeeds,
                                                 soilHealth,
                                                 overall,
                                                 lastUpdated,
                                                 getStatusColor,
                                                 getBarColor
                                             }) => {
    return (
        <Link to={`/projects/${id}`} style={{textDecoration: 'none', color: 'inherit'}}>
            <div style={card}>
                <div style={badgeRow}>
                    <span style={{...statusBadge, backgroundColor: getStatusColor(status)}}>{status}</span>
                </div>
                <h5 style={cardTitle}>{name}</h5>
                <p style={date}>Last Updated: {new Date(lastUpdated).toLocaleDateString()}</p>
                <div style={healthRow}>
                    <p style={sub}>Health</p>
                    <p style={numberOverall}>{overall}</p>
                </div>
                <div style={barContainer}>
                    <div style={{...bar, width: `${overall}%`, backgroundColor: getBarColor(overall)}}/>
                </div>
                <div style={statsRow}>
                    <p style={sub}>💧 Water Needs: {waterNeeds}</p>
                    <p style={sub}>🌱 Soil Health: {soilHealth}%</p>
                </div>
                <p style={viewButton}>View Details ➜</p>
            </div>
        </Link>
    );
};

export default ProjectCard;


const card = {
    backgroundColor: '#fff',
    padding: '16px',
    borderRadius: '12px',
    boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)',
    marginBottom: '16px',
};
const badgeRow = {display: 'flex', justifyContent: 'flex-start', marginBottom: '-20px'};
const statusBadge = {fontSize: '14px', color: '#fff', padding: '4px 8px', borderRadius: '9999px'};
const cardTitle = {fontSize: '24px', fontWeight: 700, marginBottom: '-10px', fontFamily: 'Poppins, sans-serif'};
const date = {fontSize: '16px', color: '#999', fontFamily: 'Poppins, sans-serif'};
const healthRow = {display: 'flex', justifyContent: 'space-between', alignItems: 'center'};
const numberOverall = {fontSize: '20px', color: '#1F3A93', fontWeight: 700, fontFamily: 'Poppins, sans-serif'};
const barContainer = {
    width: '100%',
    height: '8px',
    backgroundColor: '#E0E0E0',
    borderRadius: '4px',
    overflow: 'hidden',
    marginBottom: '8px'
};
const bar = {height: '100%', borderRadius: '4px', transition: 'all 0.3s ease'};
const statsRow = {display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px'};
const sub = {fontSize: '15px', color: '#666', fontFamily: 'Poppins, sans-serif'};
const viewButton = {
    color: '#1F3A93',
    fontWeight: 600,
    textAlign: 'right' as const,
    cursor: 'pointer',
    fontFamily: 'Poppins, sans-serif',
};
