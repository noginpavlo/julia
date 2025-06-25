import React, { useEffect, useState } from 'react';
import { useUser } from '../context/UserContext.jsx';
import '../assets/css/TestPage.css';

const TestPage = () => {
  const { accessToken } = useUser();
  const [quizCards, setQuizCards] = useState([]);
  const [selectedDecks, setSelectedDecks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [distributed, setDistributed] = useState(null);
  const [selectedAnswers, setSelectedAnswers] = useState({});

  useEffect(() => {
    if (selectedDecks.length === 0) return;

    const fetchQuizData = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        selectedDecks.forEach(id => params.append('deck_ids', id));

        const response = await fetch(`http://localhost:8000/api/quiz/test?${params.toString()}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
          },
          credentials: 'include',
        });

        if (!response.ok) throw new Error('Failed to fetch quiz data.');

        const data = await response.json();
        setQuizCards(data);
        setDistributed(distributeQuestionTypes(data));
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchQuizData();
  }, [selectedDecks, accessToken]);

  const handleDeckSelection = (deckId) => {
    setSelectedDecks(prev =>
      prev.includes(deckId) ? prev.filter(id => id !== deckId) : [...prev, deckId]
    );
  };

  const distributeQuestionTypes = (cards) => {
    const shuffled = [...cards].sort(() => 0.5 - Math.random());
    return {
      mcq: shuffled.slice(0, 5),
      cloze: shuffled.slice(5, 10),
      recall: shuffled.slice(10, 15),
      matching: shuffled.slice(15, 20),
    };
  };

  const getMCQOptions = (currentCard, allCards) => {
    const correctDefinition = currentCard.json_data.definitions?.[0] || 'Unknown';

    const otherDefs = allCards
      .filter(card => card.id !== currentCard.id)
      .map(card => card.json_data.definitions?.[0] || 'Unknown')
      .slice(0, 3);

    const allOptions = [...otherDefs, correctDefinition];
    return allOptions.sort(() => 0.5 - Math.random());
  };

  const handleSelectOption = (questionId, optionIndex) => {
    setSelectedAnswers(prev => ({ ...prev, [questionId]: optionIndex }));
  };

  return (
    <div id="test-page">
      <div id="test-page-container">
        <h1 className="test-page-title">Vocabulary Test</h1>

        <div className="deck-selection-section">
          <h2>Select Decks:</h2>
          <div className="deck-options">
            {[1, 2, 3].map(deckId => (
              <label key={deckId} className="deck-option">
                <input
                  type="checkbox"
                  checked={selectedDecks.includes(deckId)}
                  onChange={() => handleDeckSelection(deckId)}
                />
                Deck {deckId}
              </label>
            ))}
          </div>
        </div>

        {loading && <p className="status-message">Loading test...</p>}
        {error && <p className="status-message error">{error}</p>}

        {!loading && !error && distributed && (
          <>
            {/* Multiple Choice */}
          <section className="quiz-section">
              <h2 id="msq-title-h2">Multiple Choice Questions</h2>
              {distributed.mcq.map((card, index) => {
                const options = getMCQOptions(card, quizCards);
                const questionName = `mcq-${card.id}`;
                const letters = ['A', 'B', 'C', 'D'];

                return (
                  <div key={card.id} className="quiz-card">
                    <h3 id="msq-question-h3">
                      {index + 1}. What does "<strong id="quiz-keyword">{card.word}</strong>" mean?
                    </h3>
                    <div className="mcq-options">
                      {options.map((opt, i) => (
                        <label key={i} className="mcq-option">
                          <input
                            type="radio"
                            name={questionName}
                            value={opt}
                            className="mcq-radio-button"
                          />
                          <span className="option-label">{letters[i]}</span>
                          <span className="option-text">{opt}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                );
              })}
            </section>

            {/* Cloze Test */}
            <section className="quiz-section">
              <h2>Fill in the Blank</h2>
              {distributed.cloze.map((card, index) => (
                <div key={card.id} className="quiz-card">
                  <h3>{index + 6}. {card.json_data.definitions?.[0]}</h3>
                  <input id="fb-input-field"
                    type="text"
                    className="answer-input"
                    placeholder="Enter the correct word..."
                  />
                </div>
              ))}
            </section>

            {/* Free Recall */}
            <section className="quiz-section">
              <h2>Free Recall</h2>
              {distributed.recall.map((card, index) => (
                <div key={card.id} className="quiz-card">
                  <h3>{index + 11}. Define: "{card.word}"</h3>
                  <textarea
                    className="answer-textarea"
                    placeholder="Type your definition..."
                  ></textarea>
                </div>
              ))}
            </section>

            {/* Matching Section */}
            <section className="quiz-section">
              <h2>Matching</h2>
              <div className="matching-grid">
                <div className="column">
                  <h4>Words</h4>
                  {distributed.matching.map(card => (
                    <div key={card.id} className="matching-item">{card.word}</div>
                  ))}
                </div>
                <div className="column">
                  <h4>Definitions</h4>
                  {[...distributed.matching]
                    .sort(() => 0.5 - Math.random())
                    .map(card => (
                      <div key={card.id} className="matching-item">
                        {card.json_data.definitions?.[0]}
                      </div>
                  ))}
                </div>
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
};

export default TestPage;