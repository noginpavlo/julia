import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../assets/css/CreatePage.css';
import { useUser } from '../context/UserContext.jsx';

const CreatePage = () => {
  const { accessToken } = useUser();
  const [deckName, setDeckName] = useState('');
  const [word, setWord] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

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
          word: word
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create card');
      }

      const navigate = useNavigate();
      navigate('/create');

    } catch (error) {
      console.error('Error:', error);
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
