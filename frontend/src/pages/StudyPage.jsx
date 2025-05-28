import React, { useState, useRef, useEffect } from 'react';

export default function StudyPage() {
  const [isFlipped, setIsFlipped] = useState(false);
  const [fadeIn, setFadeIn] = useState(false);
  const cardRef = useRef(null);
  const frontRef = useRef(null);
  const backRef = useRef(null);

  const handleFlip = () => {
    setFadeIn(false);
    setIsFlipped(prev => !prev);
  };

  const handleRatingClick = () => {
    setFadeIn(false);
    setIsFlipped(false);
  };

  // Set height based on active face
  useEffect(() => {
    const currentRef = isFlipped ? backRef.current : frontRef.current;
    const height = currentRef?.offsetHeight || 0;
    if (cardRef.current) {
      cardRef.current.style.height = `${height}px`;
    }

    // Delay adding the visible class so CSS transition can trigger
    const timeout = setTimeout(() => {
      setFadeIn(true);
    }, 20); // small delay to allow opacity: 0 to register

    return () => clearTimeout(timeout);
  }, [isFlipped]);

  return (
    <section id="study">
      <div className="inner">
        <div className="flashcard-wrapper">
          <div className="flashcard" ref={cardRef}>
            {!isFlipped ? (
              <div
                className={`flashcard-face front ${fadeIn ? 'visible' : ''}`}
                ref={frontRef}
              >
                <h3 className="major">Word</h3>
                <p><strong>Word:</strong> ExampleWord</p>
                <p><strong>Phonetic:</strong> /ex·am·ple/</p>
              </div>
            ) : (
              <div
                className={`flashcard-face back ${fadeIn ? 'visible' : ''}`}
                ref={backRef}
              >
                <h3 className="major">Details</h3>
                <p><strong>Meaning 1:</strong> Lorem ipsum dolor sit amet.</p>
                <p><strong>Meaning 2:</strong> Consectetur adipiscing elit.</p>
                <p><strong>Example 1:</strong> This is a sentence using the word.</p>
                <p><strong>Example 2:</strong> Another usage in a different context.</p>
              </div>
            )}
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
