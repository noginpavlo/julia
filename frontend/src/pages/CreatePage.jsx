import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../assets/css/CreatePage.css';
import { useUser } from '../context/UserContext.jsx';
import { useNotification } from '../context/NotificationContext.jsx';

const CreatePage = () => {
  const { accessToken } = useUser();
  const { addNotification } = useNotification();
  const [deckName, setDeckName] = useState('');
  const [word, setWord] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    // 1. Show pending notification immediately
    addNotification({
      message: `The card '${word}' is being created.`,
      type: 'pending',
    });

    try {
      const response = await fetch('http://localhost:8000/api/card_manager/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        credentials: 'include',
        body: JSON.stringify({
          deck_name: deckName,
          word: word,
        }),
      });

      if (response.status === 400) {
        // 2. Show specific error message from backend if word exists
        const data = await response.json();
        addNotification({
          message: data.message || 'Word already exists in deck.',
          type: 'error',
        });
      } else if (!response.ok) {
        throw new Error('Failed to create card');
      } else {
        // Success — clear input fields, success message comes from WebSocket
        setDeckName('');
        setWord('');
      }
    } catch (error) {
      console.error('Error:', error);
      addNotification({
        message: 'Something went wrong while sending your request.',
        type: 'error',
      });
    }
  };

  return (
    <section id="create-section">
      <div className="create-card-container">
        <h2>Create a New Flashcard</h2>
        <form onSubmit={handleSubmit}>
          <div className="create-field">
            <label htmlFor="deck-name">Deck Name</label>
            <input
              type="text"
              id="deck-name"
              name="deck_name"
              placeholder="Enter deck name"
              value={deckName}
              onChange={(e) => setDeckName(e.target.value)}
              required
            />
          </div>

          <div className="create-field">
            <label htmlFor="word-input">Word</label>
            <input
              type="text"
              id="word-input"
              name="word"
              placeholder="Enter word to create card"
              value={word}
              onChange={(e) => setWord(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="create-submit-button">Create Card</button>
        </form>
      </div>
    </section>
  );
};

export default CreatePage;

