-- Q1: Each film with its views before release and its money (JOIN)
SELECT f.film_id, f.language, f.prerelease_views_7d, b.worldwide_gross_cr
FROM films f
JOIN boxoffice b ON b.film_id = f.film_id
ORDER BY b.worldwide_gross_cr DESC;

-- Q2: Number of films, average money and average views for each language (GROUP BY)
SELECT f.language,
       COUNT(*)                              AS films,
       ROUND(AVG(b.worldwide_gross_cr), 1)   AS avg_gross_cr,
       ROUND(AVG(f.prerelease_views_7d), 0)  AS avg_prerelease_views
FROM films f
JOIN boxoffice b ON b.film_id = f.film_id
GROUP BY f.language
ORDER BY avg_gross_cr DESC;

-- Q3: Money earned for every 1,000 views, for each language (JOIN and GROUP BY)
SELECT f.language,
       ROUND(SUM(b.worldwide_gross_cr) / (SUM(f.prerelease_views_7d) / 1000.0), 3) AS gross_cr_per_1k_views
FROM films f
JOIN boxoffice b ON b.film_id = f.film_id
WHERE f.prerelease_views_7d IS NOT NULL
GROUP BY f.language
ORDER BY gross_cr_per_1k_views DESC;

-- Q4: Views on release day and on day 7 for each film
SELECT d0.film_id,
       d0.views                                     AS views_release_day,
       d7.views                                     AS views_day_7,
       ROUND(1.0 * d7.views / NULLIF(d0.views,0), 2) AS day7_retention
FROM daily_buzz d0
JOIN daily_buzz d7 ON d7.film_id = d0.film_id AND d7.day_from_release = 7
WHERE d0.day_from_release = 0
ORDER BY day7_retention DESC;

-- Q5: Average critic score for each film, with its money (JOIN and GROUP BY)
SELECT c.film_id,
       COUNT(*)                          AS sentences,
       ROUND(AVG(c.vader_compound), 3)   AS avg_critic_tone,
       SUM(c.sentiment_label = 'neg')    AS negative_sentences,
       b.worldwide_gross_cr
FROM critic_sentences c
JOIN boxoffice b ON b.film_id = c.film_id
GROUP BY c.film_id, b.worldwide_gross_cr
ORDER BY avg_critic_tone DESC;

-- Q6: What critics talk about, and how positive they are (GROUP BY)
SELECT aspect, COUNT(*) AS mentions, ROUND(AVG(vader_compound), 3) AS avg_tone
FROM critic_sentences
WHERE aspect <> 'none'
GROUP BY aspect
ORDER BY mentions DESC;

-- Q7: Films whose views were highest after the first week
SELECT film_id, language, peak_day, buzz_half_life_days
FROM films
WHERE peak_day > 6
ORDER BY peak_day DESC;
