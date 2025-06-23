import React from 'react';
import { Link } from 'react-router-dom';
import createImg from '../assets/images/create.jpg';
import learnImg from '../assets/images/learn.jpg';
import chartImg from '../assets/images/chart.jpg';
import bannerImg from '../assets/images/banner.jpg';

export default function Home() {
  return (
    <>
      {/* BANNER */}
      <section id="banner" className="major">
        <div className="inner">
          <header className="major">
            <h1>Welcome to JULIA</h1>
          </header>
          <div className="content">
            <p>
              A free online tool to help you study<br />
              Make new cards fast, intensify your learning
            </p>
            <ul className="actions">
              <li><a href="#one" className="button next scrolly">Get Started</a></li>
            </ul>
          </div>
        </div>
      </section>

      {/* MAIN CONTENT */}
      <div id="main">
        {/* Section One */}
        <section id="section-one">
          <div id="section-one-grid">
            <a href="/create" className="section-one-tile" id="tile-create" style={{ backgroundImage: `url(${createImg})` }}>
              <div className="section-one-overlay"></div>
              <div className="section-one-content">
                <header className="section-one-header">
                  <h3>Create</h3>
                  <p>Make your cards easy and fast</p>
                </header>
              </div>
            </a>

            <a href="/browser/decks" className="section-one-tile" id="tile-learn" style={{ backgroundImage: `url(${learnImg})` }}>
              <div className="section-one-overlay"></div>
              <div className="section-one-content">
                <header className="section-one-header">
                  <h3>Learn</h3>
                  <p>Study your cards</p>
                </header>
              </div>
            </a>

            <a href="/stats" className="section-one-tile" id="tile-stats" style={{ backgroundImage: `url(${chartImg})` }}>
              <div className="section-one-overlay"></div>
              <div className="section-one-content">
                <header className="section-one-header">
                  <h3>Stats</h3>
                  <p>Track your progress with charts</p>
                </header>
              </div>
            </a>

            <a href="/quiz" className="section-one-tile" id="tile-quiz" style={{ backgroundImage: `url(${bannerImg})` }}>
              <div className="section-one-overlay"></div>
              <div className="section-one-content">
                <header className="section-one-header">
                  <h3>Test Yourself</h3>
                  <p>Take a quiz to test your knowledge</p>
                </header>
              </div>
            </a>
          </div>
        </section>


        {/* Section Two */}
        <section id="two">
          <div className="inner">
            <header className="major">
              <h2>Massa libero</h2>
            </header>
            <p>
                Add short project description here. The button below will lead to extended explanation page about the
                project.
            </p>
            <ul className="actions">
              <li><a href="landing.html" className="button next">Get Started</a></li>
            </ul>
          </div>
        </section>
      </div>
    </>
  );
}

function Article({ img, title, description, link }) {
  return (
    <article>
      <Link to={link} className="image-link">
        <span className="image">
          <img src={img} alt={title} />
        </span>
      </Link>
      <header className="major">
        <h3>{title}</h3>
        <p>{description}</p>
      </header>
    </article>
  );
}
