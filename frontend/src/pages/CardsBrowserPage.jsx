import React, { useEffect, useState } from "react";
import { useUser } from "../context/UserContext.jsx";
import "../assets/css/BrowserPage.css";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEye, faEdit, faTrash } from "@fortawesome/free-solid-svg-icons";

import kittyImage from "../assets/images/kitty.png";

const CardList = () => {
  const { accessToken } = useUser();
  const deckId = 1;

  const [cards, setCards] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const cardsPerPage = 10;

  const fetchCards = async (page, search, token) => {
    let url = `http://localhost:8000/api/card_manager/decks/${deckId}/cards/?page=${page}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    try {
      const response = await fetch(url, {
        headers,
        credentials: "include",
      });

      if (!response.ok) throw new Error("Failed to fetch cards");

      const data = await response.json();
      setCards(data.results);
      setTotalCount(data.count);
    } catch (error) {
      console.error("Failed to fetch cards:", error);
      setCards([]);
      setTotalCount(0);
    }
  };

  useEffect(() => {
    fetchCards(currentPage, searchQuery, accessToken);
  }, [currentPage, searchQuery, accessToken]);

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const handleDeleteCard = async (cardId) => {
    if (!window.confirm("Are you sure you want to delete this card?")) return;

    try {
      const headers = accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
      const response = await fetch(`http://localhost:8000/api/cards/${cardId}/`, {
        method: "DELETE",
        headers,
        credentials: "include",
      });

      if (response.ok) {
        setCards((prev) => prev.filter((card) => card.id !== cardId));
      } else {
        alert("Failed to delete card.");
      }
    } catch (error) {
      console.error("Error deleting card:", error);
    }
  };

  const renderPagination = () => {
    const totalPages = Math.ceil(totalCount / cardsPerPage);
    if (totalPages <= 1) return null;

    const buttons = [];

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

    buttons.push(createArrowButton("«", 1, currentPage === 1, "btn-page-first"));
    buttons.push(createArrowButton("‹", currentPage - 1, currentPage === 1, "btn-page-prev"));

    buttons.push(createPageLink("1", 1, currentPage === 1, "btn-page-1"));

    if (currentPage > 4) {
      buttons.push(<span key="dots-left" className="pagination-dots">...</span>);
    }

    const start = Math.max(2, currentPage);
    const end = Math.min(currentPage + 3, totalPages - 1);

    for (let i = start; i <= end; i++) {
      if (i !== 1 && i !== totalPages) {
        buttons.push(createPageLink(i.toString(), i, i === currentPage, `btn-page-${i}`));
      }
    }

    if (currentPage + 3 < totalPages - 1) {
      buttons.push(<span key="dots-right" className="pagination-dots">...</span>);
    }

    if (totalPages > 1) {
      buttons.push(createPageLink(totalPages.toString(), totalPages, currentPage === totalPages, `btn-page-${totalPages}`));
    }

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
          placeholder="Search cards..."
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </div>

      <ul id="deck-list">
        {cards.length === 0 ? (
          <div className="empty-container">
            <img src={kittyImage} alt="Sad Cat Illustration" className="kitty-image" />
            <h2>No cards found</h2>
            <p>We couldn't find any cards that match your search.</p>
          </div>
        ) : (
          cards.map((card) => (
            <li key={card.id} className="deck-item">
              <span className="deck-name">{card.word}</span>
              <div className="actions">
                <a className="button-link" href={`/cards/${card.id}/view/`}>
                  <button id={`btn-view-${card.id}`} title="View Card">
                    <FontAwesomeIcon icon={faEye} />
                  </button>
                </a>
                <a className="button-link" href={`/cards/${card.id}/edit/`}>
                  <button id={`btn-edit-${card.id}`} title="Edit Card">
                    <FontAwesomeIcon icon={faEdit} />
                  </button>
                </a>
                <button
                  id={`btn-delete-${card.id}`}
                  title="Delete Card"
                  onClick={() => handleDeleteCard(card.id)}
                >
                  <FontAwesomeIcon icon={faTrash} />
                </button>
              </div>
            </li>
          ))
        )}
      </ul>

      {renderPagination()}
    </div>
  );
};

export default CardList;
