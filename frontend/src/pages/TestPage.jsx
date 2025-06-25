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
  const [matches, setMatches] = useState({});
  const [draggedWordId, setDraggedWordId] = useState(null);
  const [definitions, setDefinitions] = useState([]);
  const [selectedWordId, setSelectedWordId] = useState(null);
  const [dragOverDefinitionId, setDragOverDefinitionId] = useState(null);

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

  useEffect(() => {
    if (!distributed?.matching) {
      setDefinitions([]);
      return;
    }
    const shuffled = [...distributed.matching].sort(() => 0.5 - Math.random());
    setDefinitions(shuffled);
  }, [distributed]);

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
    return [...otherDefs, correctDefinition].sort(() => 0.5 - Math.random());
  };

  const handleSelectOption = (questionId, optionIndex) => {
    setSelectedAnswers(prev => ({ ...prev, [questionId]: optionIndex }));
  };

  const matchingCards = distributed?.matching || [];
  const unmatchedWords = matchingCards.filter(wordCard => !Object.values(matches).includes(wordCard.id));

  // Drag & Drop handlers
  const handleDragStart = (wordId) => {
    setDraggedWordId(wordId);
    setSelectedWordId(null); // Clear selection on drag start
  };
  const handleDragEnd = () => {
    setDraggedWordId(null);
    setDragOverDefinitionId(null);
  };

  const handleDrop = (definitionId) => {
    if (!definitionId || !draggedWordId) return;

    setMatches(prev => {
      const newMatches = { ...prev };
      // Remove previous match for this dragged word
      for (const defId in newMatches) {
        if (newMatches[defId] === draggedWordId) {
          delete newMatches[defId];
        }
      }
      newMatches[definitionId] = draggedWordId;
      return newMatches;
    });

    setDraggedWordId(null);
    setDragOverDefinitionId(null);
  };

  const handleWordReturn = () => {
    if (!draggedWordId) return;
    setMatches(prev => {
      const newMatches = { ...prev };
      for (const defId in newMatches) {
        if (newMatches[defId] === draggedWordId) {
          delete newMatches[defId];
        }
      }
      return newMatches;
    });
    setDraggedWordId(null);
  };

  // Click-to-select handlers
  const handleWordClick = (wordId) => {
    if (draggedWordId) return; // Ignore clicks if dragging

    setSelectedWordId(prev => (prev === wordId ? null : wordId));
  };

  const handleDefinitionClick = (definitionId) => {
    if (!selectedWordId) return;

    setMatches(prev => {
      const newMatches = { ...prev };
      // Remove previous match for this selected word
      for (const defId in newMatches) {
        if (newMatches[defId] === selectedWordId) {
          delete newMatches[defId];
        }
      }
      newMatches[definitionId] = selectedWordId;
      return newMatches;
    });

    setSelectedWordId(null);
  };

  // Drag over handlers for definitions
  const handleDefinitionDragOver = (defId, e) => {
    e.preventDefault();
    setDragOverDefinitionId(defId);
  };
  const handleDefinitionDragLeave = (defId) => {
    if (dragOverDefinitionId === defId) setDragOverDefinitionId(null);
  };

  return (
    <div id="test-page">
      <div id="test-page-container">
        <h1 className="test-page-title">Vocabulary Test</h1>

        {/* Deck Selection */}
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
            {/* MCQ */}
            <section className="quiz-section">
              <h2 id="msq-title-h2">Choose the correct word definition</h2>
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
                            onChange={() => handleSelectOption(card.id, i)}
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
              <h2>Fell in the blank with a word that matches a definition</h2>
              {distributed.cloze.map((card, index) => (
                <div key={card.id} className="quiz-card">
                  <h3>{index + 6}. {card.json_data.definitions?.[0]}</h3>
                  <input
                    id="fb-input-field"
                    type="text"
                    className="answer-input"
                    placeholder="Enter the correct word..."
                  />
                </div>
              ))}
            </section>

            {/* Free Recall */}
            <section className="quiz-section">
              <h2>Put a word definition in your own words</h2>
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
              <h2>Match words and definitions by dragging and dropping or clicking</h2>
              <div className="matching-container">

                {/* Draggable Words */}
                <div
                  className="words-column"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handleWordReturn}
                >
                  {unmatchedWords.map(wordCard => {
                    const isSelected = selectedWordId === wordCard.id;
                    return (
                      <div
                        key={wordCard.id}
                        className={`matching-item word
                          ${draggedWordId === wordCard.id ? 'dragging' : ''}
                          ${isSelected ? 'selected' : ''}
                          ${selectedWordId && !isSelected ? 'subtle' : ''}
                        `}
                        draggable
                        onDragStart={() => handleDragStart(wordCard.id)}
                        onDragEnd={handleDragEnd}
                        onClick={() => handleWordClick(wordCard.id)}
                        style={{ cursor: 'pointer', userSelect: 'none' }}
                      >
                        {wordCard.word}
                      </div>
                    );
                  })}
                </div>

                {/* Definitions */}
                <div className="definitions-column">
                  {definitions.map(defCard => {
                    const matchedWordId = matches[defCard.id];
                    const matchedWord = matchingCards.find(w => w.id === matchedWordId);
                    const isDragOver = dragOverDefinitionId === defCard.id;
                    const highlightSockets = draggedWordId || selectedWordId;

                    return (
                      <div
                        key={defCard.id}
                        className={`matching-item definition ${matchedWord ? 'matched' : ''} ${isDragOver ? 'drag-over' : ''}`}
                        onDragOver={e => handleDefinitionDragOver(defCard.id, e)}
                        onDragLeave={() => handleDefinitionDragLeave(defCard.id)}
                        onDrop={e => {
                          e.preventDefault();
                          handleDrop(defCard.id);
                        }}
                        onClick={() => handleDefinitionClick(defCard.id)}
                        style={{ cursor: selectedWordId ? 'pointer' : 'default' }}
                      >
                        <div className="definition-text">{defCard.json_data.definitions?.[0]}</div>
                        <div className={`word-socket ${highlightSockets ? 'highlight-socket' : ''}`}>
                          {matchedWord ? (
                            <div
                              className="matched-word"
                              draggable
                              onDragStart={() => handleDragStart(matchedWord.id)}
                              onDragEnd={handleDragEnd}
                            >
                              {matchedWord.word}
                            </div>
                          ) : (
                            <span className="socket-placeholder">Drop here</span>
                          )}
                        </div>
                      </div>
                    );
                  })}
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
