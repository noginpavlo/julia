import React from 'react';
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
        <section id="one" className="tiles">
          <Article
            img={createImg}
            title="Create"
            description="Make your cards easy and fast"
            link="#"
          />
          <Article
            img={learnImg}
            title="Learn"
            description="Study your cards"
            link="#"
          />
          <Article
            img={chartImg}
            title="Stats"
            description="Track your progress with comprehensive charts"
            link="#"
          />
          <Article
            img={bannerImg}
            title="Test yourself"
            description="Take a quiz to put your knowledge to the test"
            link="#"
          />
        </section>

        {/* Section Two */}
        <section id="two">
          <div className="inner">
            <header className="major">
              <h2>Massa libero</h2>
            </header>
            <p>
              Nullam et orci eu lorem consequat tincidunt vivamus et sagittis libero.
              Mauris aliquet magna magna sed nunc rhoncus pharetra. Pellentesque condimentum sem.
              In efficitur ligula tate urna. Maecenas laoreet massa vel lacinia pellentesque lorem ipsum dolor.
              Nullam et orci eu lorem consequat tincidunt. Vivamus et sagittis libero.
              Mauris aliquet magna magna sed nunc rhoncus amet pharetra et feugiat tempus.
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
      <span className="image">
        <img src={img} alt="" />
      </span>
      <header className="major">
        <h3><a href={link} className="link">{title}</a></h3>
        <p>{description}</p>
      </header>
    </article>
  );
}