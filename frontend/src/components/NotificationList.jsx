import React from 'react';
import { useNotification } from '../context/NotificationContext.jsx';
import '../assets/css/NotificationList.css';

const NotificationList = () => {
  const { notifications, removeNotification } = useNotification();

  console.log("Rendering notifications:", notifications);

  return (
    <div className="notification-wrapper">
      {notifications.map((n) => (
        <div key={n.id} className={`notification ${n.type}`}>
          {n.message}
          <button onClick={() => removeNotification(n.id)}>×</button>
        </div>
      ))}
    </div>
  );
};

export default NotificationList;