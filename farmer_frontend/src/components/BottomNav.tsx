import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/BottomNav.css";

const items = [
    { name: "Home", icon: "/assets/home.png", route: "/home" },
    { name: "Projects", icon: "/assets/sprout.png", route: "/projects" },
    { name: "Profile", icon: "/assets/user.png", route: "/profile" },
    { name: "Community", icon: "/assets/people.png", route: "/community" },
    { name: "Chat", icon: "/assets/agents.png", route: "/ai" },
];

const BottomNav: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <nav className="navbar">
            {items.map((item) => {
                const isActive = location.pathname === item.route;
                return (
                    <div
                        key={item.name}
                        className="nav-item"
                        onClick={() => navigate(item.route)}
                    >
                        <img
                            src={item.icon}
                            alt={item.name}
                            className={`icon ${isActive ? "active-icon" : ""}`}
                        />
                        <span className={`label ${isActive ? "active-label" : ""}`}>
                            {item.name}
                        </span>
                        {isActive && <div className="underline" />}
                    </div>
                );
            })}
        </nav>
    );
};

export default BottomNav;
