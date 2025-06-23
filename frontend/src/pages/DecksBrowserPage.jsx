import React, { useEffect, useState } from "react";
import { useUser } from "../context/UserContext.jsx";
import "../assets/css/BrowserPage.css";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEye, faBookOpen, faTrash } from "@fortawesome/free-solid-svg-icons";

import kittyImage from '../assets/images/kitty.png';

const BrowserPage = () => {
  const { accessToken } = useUser();
  const [decks, setDecks] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const decksPerPage = 10;

  const fetchDecks = async (page, search, token) => {
    let url = `http://localhost:8000/api/card_manager/decks/?page=${page}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    try {
      const response = await fetch(url, {
        headers,
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch decks");
      }

      const data = await response.json();
      setDecks(data.results);
      setTotalCount(data.count);
    } catch (error) {
      console.error("Failed to fetch decks:", error);
      if (error.message.includes("401")) {
        setDecks([]);
        setTotalCount(0);
      }
    }
  };

  useEffect(() => {
    fetchDecks(currentPage, searchQuery, accessToken);
  }, [currentPage, searchQuery, accessToken]);

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const handleDeleteDeck = async (deckId) => {
    if (!window.confirm("Are you sure you want to delete this deck?")) return;

    try {
      const headers = accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
      const response = await fetch(`/api/card_manager/decks/${deckId}/`, {
        method: "DELETE",
        headers,
        credentials: "include",
      });

      if (response.ok) {
        setDecks((prev) => prev.filter((deck) => deck.id !== deckId));
      } else {
        alert("Failed to delete deck.");
      }
    } catch (error) {
      console.error("Error deleting deck:", error);
    }
  };

const renderPagination = () => {
  const totalPages = Math.ceil(totalCount / decksPerPage);
  if (totalPages <= 1) return null;

  const buttons = [];

  // For arrows, keep buttons
  const createArrowButton = (label, page, disabled = false, id = "") => (
    <button
      key={label + "-" + page}
      onClick={() => setCurrentPage(page)}
      disabled={disabled}
      id={id}
      className="pagination-arrow"
      aria-label={label}
    >
      {label}
    </button>
  );

  // For page numbers, use links
  const createPageLink = (label, page, isCurrent = false, id = "") => (
    <a
      key={label + "-" + page}
      href="#"
      onClick={(e) => {
        e.preventDefault();
        if (!isCurrent) setCurrentPage(page);
      }}
      className={`pagination-page-number${isCurrent ? " current-page" : ""}`}
      id={id}
      aria-current={isCurrent ? "page" : undefined}
      tabIndex={isCurrent ? -1 : 0}
    >
      {label}
    </a>
  );

  // Arrows « First, ‹ Prev
  buttons.push(createArrowButton("«", 1, currentPage === 1, "btn-page-first"));
  buttons.push(createArrowButton("‹", currentPage - 1, currentPage === 1, "btn-page-prev"));

  // Always show page 1 as link
  buttons.push(createPageLink("1", 1, currentPage === 1, "btn-page-1"));

  // Show "..." if currentPage > 4
  if (currentPage > 4) {
    buttons.push(<span key="dots-left" className="pagination-dots">...</span>);
  }

  // Middle pages
  const start = Math.max(2, currentPage);
  const end = Math.min(currentPage + 3, totalPages - 1);

  for (let i = start; i <= end; i++) {
    if (i !== 1 && i !== totalPages) {
      buttons.push(createPageLink(i.toString(), i, i === currentPage, `btn-page-${i}`));
    }
  }

  // Show "..." if gap before last page
  if (currentPage + 3 < totalPages - 1) {
    buttons.push(<span key="dots-right" className="pagination-dots">...</span>);
  }

  // Last page as link if > 1
  if (totalPages > 1) {
    buttons.push(createPageLink(totalPages.toString(), totalPages, currentPage === totalPages, `btn-page-${totalPages}`));
  }

  // Arrows › Next, » Last
  buttons.push(createArrowButton("›", currentPage + 1, currentPage === totalPages, "btn-page-next"));
  buttons.push(createArrowButton("»", totalPages, currentPage === totalPages, "btn-page-last"));

  return <div className="pagination">{buttons}</div>;
};

  return (
    <div className="deck-browser-page">
      <div className="search-container">
        <input
          type="text"
          className="search-input"
          placeholder="Search for a deck..."
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </div>

      <ul id="deck-list">
        {decks.length === 0 ? (
          <div className="empty-container">
            <img src={kittyImage} alt="Sad Cat Illustration" className="kitty-image" />
            <h2>No decks found</h2>
            <p>We couldn't find any decks that match your search.</p>
          </div>
        ) : (
          decks.map((deck) => (
            <li key={deck.id} className="deck-item">
              <span className="deck-name">{deck.deck_name}</span>
              <div className="actions">
                <a className="button-link" href={`/decks/${deck.id}/cards/`}>
                  <button id={`btn-view-${deck.id}`} title="View Cards">
                    <FontAwesomeIcon icon={faEye} />
                  </button>
                </a>
                <a className="button-link" href={`/learn/${deck.id}/`}>
                  <button id={`btn-learn-${deck.id}`} title="Learn Deck">
                    <FontAwesomeIcon icon={faBookOpen} />
                  </button>
                </a>
                <button
                  id={`btn-delete-${deck.id}`}
                  title="Delete Deck"
                  onClick={() => handleDeleteDeck(deck.id)}
                >
                  <FontAwesomeIcon icon={faTrash} />
                </button>
              </div>
            </li>
          ))
        )}
      </ul>

      {/* Render full pagination bar here */}
      {renderPagination()}
    </div>
  );
};

export default BrowserPage;
