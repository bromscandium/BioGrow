import React from "react";
import "../styles/Header.css";

const Header: React.FC = () => {
    return (
        <header className="header-container">
            <div className="header">
                <h1 className="logo">BioGrow 🌿</h1>
            </div>
        </header>
    );
};

export default Header;