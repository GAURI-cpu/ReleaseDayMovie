# SQL results (output of each query)

Row counts: `films` = 25, `boxoffice` = 25, `daily_buzz` = 2201, `critic_sentences` = 217


## Q1: Each film with its views before release and its money (JOIN)

```sql
SELECT f.film_id, f.language, f.prerelease_views_7d, b.worldwide_gross_cr
FROM films f
JOIN boxoffice b ON b.film_id = f.film_id
ORDER BY b.worldwide_gross_cr DESC;
```

| film_id                      | language   |   prerelease_views_7d |   worldwide_gross_cr |
|:-----------------------------|:-----------|----------------------:|---------------------:|
| dhurandhar_2025              | Hindi      |                258412 |              1350.83 |
| chhaava_2025                 | Hindi      |                185118 |               797.34 |
| saiyaara_2025                | Hindi      |                   nan |               579.23 |
| coolie_2025                  | Tamil      |                452527 |               509.5  |
| war_2_2025                   | Hindi      |                278977 |               327    |
| lokah_chapter_1_chandra_2025 | Malayalam  |                 42445 |               303    |
| mahavatar_narsimha_2025      | Hindi      |                  3370 |               300.82 |
| they_call_him_og_2025        | Telugu     |                221267 |               295    |
| l2_empuraan_2025             | Malayalam  |                331916 |               268.05 |
| sankranthiki_vasthunam_2025  | Telugu     |                 38966 |               260    |
| thudarum_2025                | Malayalam  |                 26067 |               238    |
| good_bad_ugly_2025           | Tamil      |                134394 |               224.12 |
| game_changer_2025            | Telugu     |                271378 |               195    |
| mirai_2025                   | Telugu     |                 24301 |               190    |
| sarvam_maya_2025             | Malayalam  |                 20415 |               153    |
| dragon_2025                  | Tamil      |                 85990 |               150    |
| su_from_so_2025              | Kannada    |                   nan |               125    |
| kuberaa_2025                 | Telugu     |                119274 |               123.5  |
| dude_2025                    | Tamil      |                118533 |               106.62 |
| tourist_family_2025          | Tamil      |                 22625 |                90    |
| kalamkaval_2025              | Malayalam  |                 34888 |                85.2  |
| mark_2025                    | Kannada    |                  7772 |                51.3  |
| the_devil_2025               | Kannada    |                 28971 |                43    |
| 45_2025                      | Kannada    |                 27132 |                21    |
| junior_2025                  | Kannada    |                   nan |                16    |


## Q2: Number of films, average money and average views for each language (GROUP BY)

```sql
SELECT f.language,
       COUNT(*)                              AS films,
       ROUND(AVG(b.worldwide_gross_cr), 1)   AS avg_gross_cr,
       ROUND(AVG(f.prerelease_views_7d), 0)  AS avg_prerelease_views
FROM films f
JOIN boxoffice b ON b.film_id = f.film_id
GROUP BY f.language
ORDER BY avg_gross_cr DESC;
```

| language   |   films |   avg_gross_cr |   avg_prerelease_views |
|:-----------|--------:|---------------:|-----------------------:|
| Hindi      |       5 |          671   |                 181469 |
| Tamil      |       5 |          216   |                 162814 |
| Telugu     |       5 |          212.7 |                 135037 |
| Malayalam  |       5 |          209.5 |                  91146 |
| Kannada    |       5 |           51.3 |                  21292 |


## Q3: Money earned for every 1,000 views, for each language (JOIN and GROUP BY)

```sql
SELECT f.language,
       ROUND(SUM(b.worldwide_gross_cr) / (SUM(f.prerelease_views_7d) / 1000.0), 3) AS gross_cr_per_1k_views
FROM films f
JOIN boxoffice b ON b.film_id = f.film_id
WHERE f.prerelease_views_7d IS NOT NULL
GROUP BY f.language
ORDER BY gross_cr_per_1k_views DESC;
```

| language   |   gross_cr_per_1k_views |
|:-----------|------------------------:|
| Hindi      |                   3.824 |
| Malayalam  |                   2.298 |
| Kannada    |                   1.805 |
| Telugu     |                   1.575 |
| Tamil      |                   1.327 |


## Q4: Views on release day and on day 7 for each film

```sql
SELECT d0.film_id,
       d0.views                                     AS views_release_day,
       d7.views                                     AS views_day_7,
       ROUND(1.0 * d7.views / NULLIF(d0.views,0), 2) AS day7_retention
FROM daily_buzz d0
JOIN daily_buzz d7 ON d7.film_id = d0.film_id AND d7.day_from_release = 7
WHERE d0.day_from_release = 0
ORDER BY day7_retention DESC;
```

| film_id                      |   views_release_day |   views_day_7 |   day7_retention |
|:-----------------------------|--------------------:|--------------:|-----------------:|
| tourist_family_2025          |                4842 |         39503 |             8.16 |
| junior_2025                  |                1294 |         10060 |             7.77 |
| saiyaara_2025                |               57286 |        335347 |             5.85 |
| mahavatar_narsimha_2025      |                3301 |         14992 |             4.54 |
| lokah_chapter_1_chandra_2025 |               72608 |        164549 |             2.27 |
| dhurandhar_2025              |              260308 |        541681 |             2.08 |
| mirai_2025                   |               33691 |         47479 |             1.41 |
| chhaava_2025                 |              231322 |        279595 |             1.21 |
| sankranthiki_vasthunam_2025  |               20034 |         18109 |             0.9  |
| sarvam_maya_2025             |               33049 |         27127 |             0.82 |
| dragon_2025                  |              102854 |         75252 |             0.73 |
| thudarum_2025                |               71526 |         50008 |             0.7  |
| kalamkaval_2025              |               35916 |         23065 |             0.64 |
| mark_2025                    |                4748 |          3058 |             0.64 |
| dude_2025                    |              115903 |         70625 |             0.61 |
| 45_2025                      |               20443 |         11050 |             0.54 |
| kuberaa_2025                 |              119159 |         54264 |             0.46 |
| war_2_2025                   |              370630 |        172087 |             0.46 |
| coolie_2025                  |              547830 |        242877 |             0.44 |
| good_bad_ugly_2025           |              185522 |         79954 |             0.43 |
| l2_empuraan_2025             |              263895 |        106621 |             0.4  |
| they_call_him_og_2025        |              228493 |         83167 |             0.36 |
| game_changer_2025            |              320455 |        106702 |             0.33 |
| the_devil_2025               |               40721 |         11370 |             0.28 |


## Q5: Average critic score for each film, with its money (JOIN and GROUP BY)

```sql
SELECT c.film_id,
       COUNT(*)                          AS sentences,
       ROUND(AVG(c.vader_compound), 3)   AS avg_critic_tone,
       SUM(c.sentiment_label = 'neg')    AS negative_sentences,
       b.worldwide_gross_cr
FROM critic_sentences c
JOIN boxoffice b ON b.film_id = c.film_id
GROUP BY c.film_id, b.worldwide_gross_cr
ORDER BY avg_critic_tone DESC;
```

| film_id                      |   sentences |   avg_critic_tone |   negative_sentences |   worldwide_gross_cr |
|:-----------------------------|------------:|------------------:|---------------------:|---------------------:|
| they_call_him_og_2025        |           9 |             0.664 |                    0 |               295    |
| dude_2025                    |           8 |             0.649 |                    1 |               106.62 |
| tourist_family_2025          |           4 |             0.538 |                    0 |                90    |
| game_changer_2025            |          16 |             0.53  |                    0 |               195    |
| kuberaa_2025                 |          10 |             0.518 |                    1 |               123.5  |
| su_from_so_2025              |           7 |             0.512 |                    1 |               125    |
| thudarum_2025                |           8 |             0.489 |                    1 |               238    |
| saiyaara_2025                |          10 |             0.39  |                    3 |               579.23 |
| mahavatar_narsimha_2025      |          13 |             0.362 |                    2 |               300.82 |
| dragon_2025                  |          10 |             0.327 |                    1 |               150    |
| lokah_chapter_1_chandra_2025 |           7 |             0.279 |                    2 |               303    |
| l2_empuraan_2025             |          15 |             0.228 |                    4 |               268.05 |
| coolie_2025                  |          11 |             0.186 |                    4 |               509.5  |
| good_bad_ugly_2025           |          13 |             0.144 |                    4 |               224.12 |
| chhaava_2025                 |          14 |             0.103 |                    6 |               797.34 |
| kalamkaval_2025              |          13 |             0.042 |                    4 |                85.2  |
| dhurandhar_2025              |          22 |             0.029 |                    9 |              1350.83 |
| the_devil_2025               |           6 |            -0.084 |                    3 |                43    |
| war_2_2025                   |          21 |            -0.12  |                   11 |               327    |


## Q6: What critics talk about, and how positive they are (GROUP BY)

```sql
SELECT aspect, COUNT(*) AS mentions, ROUND(AVG(vader_compound), 3) AS avg_tone
FROM critic_sentences
WHERE aspect <> 'none'
GROUP BY aspect
ORDER BY mentions DESC;
```

| aspect     |   mentions |   avg_tone |
|:-----------|-----------:|-----------:|
| story      |         51 |      0.184 |
| acting     |         39 |      0.385 |
| music      |         16 |      0.306 |
| vfx_action |         10 |      0.163 |
| direction  |          9 |      0.528 |
| length     |          6 |      0.162 |


## Q7: Films whose views were highest after the first week

```sql
SELECT film_id, language, peak_day, buzz_half_life_days
FROM films
WHERE peak_day > 6
ORDER BY peak_day DESC;
```

| film_id                     | language   |   peak_day |   buzz_half_life_days |
|:----------------------------|:-----------|-----------:|----------------------:|
| sankranthiki_vasthunam_2025 | Telugu     |         47 |                     2 |
| sarvam_maya_2025            | Malayalam  |         37 |                     4 |
| tourist_family_2025         | Tamil      |         34 |                     8 |
| mark_2025                   | Kannada    |         29 |                     4 |
| mahavatar_narsimha_2025     | Hindi      |         16 |                    10 |
| dhurandhar_2025             | Hindi      |          9 |                    16 |
| su_from_so_2025             | Kannada    |          9 |                    10 |
