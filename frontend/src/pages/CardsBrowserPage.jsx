import React, { useState, useEffect, useCallback } from "react";
import { useUser } from "../context/UserContext.jsx";

const PAGE_SIZE = 10;

const CardBrowserPage = () => {
  const { accessToken } = useUser();
  const [deckId, setDeckId] = useState(null);
  const [cards, setCards] = useState([]);
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [totalPages, setTotalPages] = useState(1);
  const [previous, setPrevious] = useState(null);
  const [next, setNext] = useState(null);

  // Extract deckId from URL
  useEffect(() => {
    const parts = window.location.pathname.split("/");
    if (parts.length >= 3) {
      setDeckId(parts[2]);
    }
  }, []);

  const getCSRFToken = () => {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      const [key, value] = cookie.trim().split("=");
      if (key === name) return decodeURIComponent(value);
    }
    return "";
  };

  const fetchCards = useCallback(async () => {
    if (!deckId) return;

    setLoading(true);

    const baseUrl = `http://localhost:8000/api/decks/${deckId}/cards/`;
    const params = new URLSearchParams();
    params.append("page", currentPage);
    if (search) params.append("search", search);

    try {
      const response = await fetch(`${baseUrl}?${params.toString()}`, {
        headers: {
          Authorization: accessToken ? `Bearer ${accessToken}` : undefined,
          "X-CSRFToken": getCSRFToken(),
        },
        credentials: "include",
      });

      if (!response.ok) throw new Error("Failed to fetch cards");

      const data = await response.json();
      setCards(data.results);
      setTotalCount(data.count);
      setTotalPages(data.total_pages || Math.ceil(data.count / PAGE_SIZE));
      setPrevious(data.previous);
      setNext(data.next);
    } catch (err) {
      console.error(err);
      setCards([]);
      setTotalCount(0);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  }, [deckId, currentPage, search, accessToken]);

  useEffect(() => {
    fetchCards();
  }, [fetchCards]);

  const handleDelete = async (cardId) => {
    if (!confirm("Delete this card?")) return;

    try {
      const res = await fetch(`http://localhost:8000/api/cards/${cardId}/`, {
        method: "DELETE",
        headers: {
          Authorization: accessToken ? `Bearer ${accessToken}` : undefined,
          "X-CSRFToken": getCSRFToken(),
        },
        credentials: "include",
      });

      if (res.ok) {
        setCards((prev) => prev.filter((card) => card.id !== cardId));
        setTotalCount((count) => count - 1);
      } else {
        alert("Failed to delete card.");
      }
    } catch (error) {
      console.error("Error deleting card:", error);
    }
  };

  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const buttons = [];

    const addPageButton = (label, page, disabled = false, current = false) => (
      <button
        key={label}
        disabled={disabled}
        className={current ? "pagination-btn current" : "pagination-btn"}
        onClick={() => setCurrentPage(page)}
      >
        {label}
      </button>
    );

    buttons.push(addPageButton("« First", 1, currentPage === 1));
    buttons.push(addPageButton("‹ Prev", currentPage - 1, currentPage === 1));

    const range = [...Array(totalPages).keys()].map((i) => i + 1);
    const visible = range.filter(
      (i) =>
        i === 1 ||
        i === totalPages ||
        Math.abs(i - currentPage) <= 1
    );

    visible.forEach((i, idx) => {
      if (idx > 0 && visible[idx - 1] !== i - 1) {
        buttons.push(<span key={`ellipsis-${i}`}>...</span>);
      }
      buttons.push(addPageButton(i, i, false, i === currentPage));
    });

    buttons.push(addPageButton("Next ›", currentPage + 1, currentPage === totalPages));
    buttons.push(addPageButton("Last »", totalPages, currentPage === totalPages));

    return <div className="pagination">{buttons}</div>;
  };

  return (
    <div>
      <div className="search-container">
        <input
          className="search-input"
          type="text"
          placeholder="Search cards..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setCurrentPage(1);
          }}
        />
      </div>

      <ul id="card-list">
        {loading ? (
          <p>Loading cards...</p>
        ) : cards.length === 0 ? (
          <div className="empty-container">
            <img src="/static/images/kitty.png" alt="Sad Cat Illustration" />
            <h2>No cards yet</h2>
            <p>This deck doesn't have any cards yet. How about creating your first one?</p>
            <a href="/create-card/">
              <button className="create-button">➕ Add Your First Card</button>
            </a>
          </div>
        ) : (
          cards.map((card) => (
            <li key={card.id} className="card-item">
              <span className="card-word">{card.word}</span>
              <div className="actions">
                <a className="button-link" href={`/cards/${card.id}/view/`}>
                  <button className="circle-button btn-view">👁️</button>
                </a>
                <a className="button-link" href={`/cards/${card.id}/edit/`}>
                  <button className="circle-button btn-edit">✏️</button>
                </a>
                <button
                  className="circle-button btn-delete"
                  onClick={() => handleDelete(card.id)}
                >
                  🗑️
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

export default CardBrowserPage;