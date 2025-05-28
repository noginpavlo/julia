import React from 'react';
import '../assets/css/CreatePage.css';


const CreatePage = () => {
  return (
    <section id="create-section">
      <div className="create-card-container">
        <h2>Create a New Flashcard</h2>

        <form method="POST" action="/create-cards">
          <div className="create-field">
            <label htmlFor="deck-name">Deck Name</label>
            <input
              type="text"
              id="deck-name"
              name="deck_name"
              placeholder="Enter deck name"
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
