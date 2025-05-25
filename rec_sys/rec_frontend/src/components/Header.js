// src/components/Header.js
import React, { useContext } from 'react';
import { AuthContext } from '../AuthContext';
import ProfilePopup from './ProfilePopup';

function Header() {
    const { user, logout } = useContext(AuthContext);
    const [showPopup, setShowPopup] = useState(false);

    return (
        <header>
            {user ? (
                <div className="user-info" onClick={() => setShowPopup(!showPopup)}>
                    <span>{user.full_name || user.username}</span>
                    {showPopup && <ProfilePopup user={user} onLogout={logout} />}
                </div>
            ) : (
                <Login />
            )}
        </header>
    );
}