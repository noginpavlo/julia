import React, { useEffect, useState } from "react";
import { useUser } from '../context/UserContext.jsx';
import "../assets/css/DecksBrowserPage.css";

const BrowserPage = () => {
  const { accessToken } = useUser();
  const [decks, setDecks] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const decksPerPage = 10;

  // Keep track of last fetch parameters to avoid infinite loops
  const [lastFetchParams, setLastFetchParams] = useState({ page: 1, search: "" });

  const fetchDecks = async (page, search, token) => {
    let url = 'http://localhost:8000/api/card_manager/decks/';
    if (search) url += `?search=${encodeURIComponent(search)}`;

    const headers = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

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
      setLastFetchParams({ page, search });
    } catch (error) {
      console.error("Failed to fetch decks:", error);
      // Optionally clear decks if unauthorized or other error?
      if (error.message.includes("401")) {
        setDecks([]);
        setTotalCount(0);
      }
    }
  };

  // Run fetch on page or search change
  useEffect(() => {
    fetchDecks(currentPage, searchQuery, accessToken);
  }, [currentPage, searchQuery, accessToken]);

  // To avoid calling fetchDecks multiple times unnecessarily, you can also:
  //  - add debounce on search input
  //  - add a loading state, etc.

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1); // reset to first page on new search
  };

  const handleDeleteDeck = async (deckId) => {
    if (!window.confirm("Are you sure you want to delete this deck?")) return;

    try {
      const headers = {};
      if (accessToken) {
        headers["Authorization"] = `Bearer ${accessToken}`;
      }

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

  // Pagination rendering code remains unchanged
  const renderPagination = () => {
    const totalPages = Math.ceil(totalCount / decksPerPage);
    const buttons = [];

    const createButton = (label, page, disabled = false, isCurrent = false) => (
      <button
        key={label}
        disabled={disabled}
        style={{
          fontWeight: isCurrent ? "bold" : "normal",
          backgroundColor: isCurrent ? "#ddd" : undefined,
        }}
        onClick={() => setCurrentPage(page)}
      >
        {label}
      </button>
    );

    buttons.push(createButton("« First", 1, currentPage === 1));
    buttons.push(createButton("‹ Prev", currentPage - 1, currentPage === 1));

    let start = Math.max(1, currentPage - 2);
    let end = Math.min(start + 4, totalPages);
    if (end - start < 4) start = Math.max(1, end - 4);

    for (let i = start; i <= end; i++) {
      buttons.push(createButton(i, i, false, i === currentPage));
    }

    buttons.push(createButton("Next ›", currentPage + 1, currentPage === totalPages));
    buttons.push(createButton("Last »", totalPages, currentPage === totalPages));

    return <div className="pagination">{buttons}</div>;
  };

  return (
    <div>
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
            <img src="/static/images/kitty.png" alt="Sad Cat Illustration" />
            <h2>No decks found</h2>
            <p>We couldn't find any decks that match your search.</p>
          </div>
        ) : (
          decks.map((deck) => (
            <li key={deck.id} className="deck-item">
              <span className="deck-name">{deck.deck_name}</span>
              <div className="actions">
                <a className="button-link" href={`/decks/${deck.id}/cards/`}>
                  <button className="circle-button btn-view" title="View Cards">
                    👁️
                  </button>
                </a>
                <a className="button-link" href={`/learn/${deck.id}/`}>
                  <button className="circle-button btn-learn" title="Learn Deck">
                    📚
                  </button>
                </a>
                <button
                  className="circle-button btn-delete"
                  title="Delete Deck"
                  onClick={() => handleDeleteDeck(deck.id)}
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

export default BrowserPage;
