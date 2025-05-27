import React, { useState, useRef, useEffect } from 'react';

export default function StudyPage() {
  const [isFlipped, setIsFlipped] = useState(false);
  const cardRef = useRef(null);
  const frontRef = useRef(null);
  const backRef = useRef(null);

  const handleFlip = () => setIsFlipped(!isFlipped);
  const handleRatingClick = () => setIsFlipped(false);

  // Dynamically set height to match tallest face
  useEffect(() => {
    const frontHeight = frontRef.current?.offsetHeight || 0;
    const backHeight = backRef.current?.offsetHeight || 0;
    const maxHeight = Math.max(frontHeight, backHeight);
    if (cardRef.current) {
      cardRef.current.style.height = `${maxHeight}px`;
    }
  }, [isFlipped]);

  return (
    <section id="study">
      <div className="inner">
        <header className="major">
          <h2>Flashcard Study</h2>
          <p>Flip the card to reveal the meaning and examples.</p>
        </header>

        <div className="flashcard-wrapper">
          <div className={`flashcard ${isFlipped ? 'flipped' : ''}`} ref={cardRef}>
            <div className="flashcard-face front" ref={frontRef}>
              <h3 className="major">Word</h3>
              <p><strong>Word:</strong> ExampleWord</p>
              <p><strong>Phonetic:</strong> /ex·am·ple/</p>
            </div>

            <div className="flashcard-face back" ref={backRef}>
              <h3 className="major">Details</h3>
              <p><strong>Meaning 1:</strong> Lorem ipsum dolor sit amet.</p>
              <p><strong>Meaning 2:</strong> Consectetur adipiscing elit.</p>
              <p><strong>Example 1:</strong> This is a sentence using the word.</p>
              <p><strong>Example 2:</strong> Another usage in a different context.</p>
            </div>
          </div>

          <div className="flashcard-actions">
            {!isFlipped ? (
              <button className="button primary" onClick={handleFlip}>
                Flip Card
              </button>
            ) : (
              <>
                <button className="button" onClick={handleRatingClick}>Again</button>
                <button className="button" onClick={handleRatingClick}>Easy</button>
                <button className="button" onClick={handleRatingClick}>Medium</button>
                <button className="button" onClick={handleRatingClick}>Hard</button>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
