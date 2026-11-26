CREATE DATABASE IF NOT EXISTS release_day_radar CHARACTER SET utf8mb4;
USE release_day_radar;

DROP TABLE IF EXISTS critic_sentences;
DROP TABLE IF EXISTS daily_buzz;
DROP TABLE IF EXISTS boxoffice;
DROP TABLE IF EXISTS films;

CREATE TABLE films (
    film_id              VARCHAR(60)  PRIMARY KEY,
    wiki_title           VARCHAR(120) NOT NULL,
    language             VARCHAR(20)  NOT NULL,
    release_date         DATE,
    runtime_min          SMALLINT,
    budget_cr            DECIMAL(8,2) NULL,
    opening_day_cr       DECIMAL(8,2) NULL,
    prerelease_views_7d  INT NULL,
    release_week_views   INT,
    peak_day             SMALLINT,
    buzz_half_life_days  SMALLINT NULL
);

CREATE TABLE boxoffice (
    film_id              VARCHAR(60) PRIMARY KEY,
    gross_raw            VARCHAR(60),
    worldwide_gross_cr   DECIMAL(9,2),
    source_page          VARCHAR(80),
    FOREIGN KEY (film_id) REFERENCES films(film_id)
);

CREATE TABLE daily_buzz (
    film_id              VARCHAR(60),
    buzz_date            DATE,
    day_from_release     SMALLINT,
    views                INT,
    edits                INT,
    PRIMARY KEY (film_id, buzz_date),
    FOREIGN KEY (film_id) REFERENCES films(film_id)
);

CREATE TABLE critic_sentences (
    sentence_id          INT AUTO_INCREMENT PRIMARY KEY,
    film_id              VARCHAR(60),
    sentence_text        TEXT,
    vader_compound       DECIMAL(5,4),
    sentiment_label      VARCHAR(8),
    aspect               VARCHAR(20),
    FOREIGN KEY (film_id) REFERENCES films(film_id)
);
