-- ============================================================
-- CRICKET DATA ANALYSIS - 20 SQL QUERIES
-- ============================================================

-- 1. Top 10 batsmen by total runs across all formats
SELECT 
    batter,
    COUNT(*) as balls_faced,
    SUM(batter_runs) as total_runs,
    ROUND(AVG(batter_runs), 2) as strike_rate,
    COUNT(CASE WHEN batter_runs = 4 THEN 1 END) as fours,
    COUNT(CASE WHEN batter_runs = 6 THEN 1 END) as sixes
FROM deliveries 
WHERE batter IS NOT NULL
GROUP BY batter
ORDER BY total_runs DESC
LIMIT 10;

-- 2. Top 10 bowlers by wickets taken
SELECT 
    bowler,
    COUNT(*) as balls_bowled,
    SUM(total_runs) as runs_conceded,
    COUNT(CASE WHEN wicket_type IS NOT NULL THEN 1 END) as wickets,
    ROUND(SUM(total_runs) * 1.0 / COUNT(*) * 6, 2) as economy_rate
FROM deliveries 
WHERE bowler IS NOT NULL
GROUP BY bowler
HAVING wickets > 0
ORDER BY wickets DESC, economy_rate ASC
LIMIT 10;

-- 3. Team performance by format
SELECT 
    m.format,
    m.team1 as team,
    COUNT(*) as matches_played,
    SUM(CASE WHEN m.winner = m.team1 THEN 1 ELSE 0 END) as wins,
    ROUND(SUM(CASE WHEN m.winner = m.team1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as win_percentage
FROM matches m
GROUP BY m.format, m.team1
UNION ALL
SELECT 
    m.format,
    m.team2 as team,
    COUNT(*) as matches_played,
    SUM(CASE WHEN m.winner = m.team2 THEN 1 ELSE 0 END) as wins,
    ROUND(SUM(CASE WHEN m.winner = m.team2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as win_percentage
FROM matches m
GROUP BY m.format, m.team2
ORDER BY format, win_percentage DESC;

-- 4. Highest team totals by format
SELECT 
    m.format,
    i.batting_team,
    m.venue,
    m.date,
    i.total_runs,
    i.total_wickets,
    i.total_overs
FROM innings i
JOIN matches m ON i.match_id = m.match_id
WHERE i.innings_number = 1
ORDER BY i.total_runs DESC
LIMIT 15;

-- 5. Most sixes hit by batsmen
SELECT 
    batter,
    COUNT(*) as sixes,
    SUM(batter_runs) as runs_from_sixes
FROM deliveries 
WHERE batter_runs = 6
GROUP BY batter
ORDER BY sixes DESC
LIMIT 10;

-- 6. Best bowling figures (most wickets in an innings)
SELECT 
    d.bowler,
    d.match_id,
    m.format,
    m.venue,
    COUNT(*) as wickets_taken,
    SUM(d.total_runs) as runs_conceded
FROM deliveries d
JOIN matches m ON d.match_id = m.match_id
WHERE d.wicket_type IS NOT NULL
GROUP BY d.bowler, d.match_id, d.innings_number
ORDER BY wickets_taken DESC, runs_conceded ASC
LIMIT 10;

-- 7. Venue analysis - highest scoring venues
SELECT 
    m.venue,
    m.city,
    COUNT(DISTINCT m.match_id) as matches_played,
    ROUND(AVG(i.total_runs), 2) as avg_runs_per_innings,
    MAX(i.total_runs) as highest_score
FROM matches m
JOIN innings i ON m.match_id = i.match_id
WHERE m.venue IS NOT NULL
GROUP BY m.venue, m.city
HAVING matches_played >= 2
ORDER BY avg_runs_per_innings DESC;

-- 8. Toss impact analysis
SELECT 
    format,
    COUNT(*) as total_matches,
    SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) as toss_winner_won,
    ROUND(SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as toss_win_percentage
FROM matches 
WHERE toss_winner IS NOT NULL AND winner IS NOT NULL
GROUP BY format;

-- 9. Most common dismissal types
SELECT 
    wicket_type,
    COUNT(*) as frequency,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM deliveries WHERE wicket_type IS NOT NULL), 2) as percentage
FROM deliveries 
WHERE wicket_type IS NOT NULL
GROUP BY wicket_type
ORDER BY frequency DESC;

-- 10. Batsmen with highest strike rates (minimum 100 balls)
SELECT 
    batter,
    COUNT(*) as balls_faced,
    SUM(batter_runs) as runs_scored,
    ROUND(SUM(batter_runs) * 100.0 / COUNT(*), 2) as strike_rate
FROM deliveries 
WHERE batter IS NOT NULL
GROUP BY batter
HAVING balls_faced >= 100
ORDER BY strike_rate DESC
LIMIT 10;

-- 11. Teams with most wins by result type
SELECT 
    winner,
    result_type,
    COUNT(*) as wins,
    ROUND(AVG(result_margin), 2) as avg_margin
FROM matches 
WHERE winner IS NOT NULL AND result_type IS NOT NULL
GROUP BY winner, result_type
ORDER BY wins DESC;

-- 12. Player of the match awards
SELECT 
    player_of_match,
    COUNT(*) as awards,
    COUNT(DISTINCT format) as formats_played
FROM matches 
WHERE player_of_match IS NOT NULL
GROUP BY player_of_match
ORDER BY awards DESC
LIMIT 10;

-- 13. Extras analysis by format
SELECT 
    m.format,
    COUNT(DISTINCT d.match_id) as matches,
    SUM(d.extras_runs) as total_extras,
    ROUND(AVG(d.extras_runs), 2) as avg_extras_per_delivery,
    COUNT(CASE WHEN d.extras_type = 'wide' THEN 1 END) as wides,
    COUNT(CASE WHEN d.extras_type = 'noball' THEN 1 END) as noballs
FROM deliveries d
JOIN matches m ON d.match_id = m.match_id
GROUP BY m.format
ORDER BY total_extras DESC;

-- 14. Most productive partnerships (batting pairs)
SELECT 
    d1.batter,
    d1.non_striker,
    d1.batting_team,
    SUM(d1.total_runs) as partnership_runs,
    COUNT(*) as balls_together
FROM deliveries d1
WHERE d1.batter IS NOT NULL AND d1.non_striker IS NOT NULL
GROUP BY d1.batter, d1.non_striker, d1.batting_team, d1.match_id, d1.innings_number
HAVING balls_together >= 20
ORDER BY partnership_runs DESC
LIMIT 15;

-- 15. Format-wise performance comparison
SELECT 
    format,
    COUNT(*) as total_matches,
    ROUND(AVG(total_runs), 2) as avg_score_per_innings,
    MAX(total_runs) as highest_score,
    MIN(total_runs) as lowest_score,
    ROUND(AVG(total_overs), 2) as avg_overs_per_innings
FROM matches m
JOIN innings i ON m.match_id = i.match_id
GROUP BY format
ORDER BY avg_score_per_innings DESC;

-- 16. Most economical bowlers (minimum 50 balls)
SELECT 
    bowler,
    COUNT(*) as balls_bowled,
    SUM(total_runs) as runs_conceded,
    ROUND(SUM(total_runs) * 6.0 / COUNT(*), 2) as economy_rate,
    COUNT(CASE WHEN wicket_type IS NOT NULL THEN 1 END) as wickets
FROM deliveries 
WHERE bowler IS NOT NULL
GROUP BY bowler
HAVING balls_bowled >= 50
ORDER BY economy_rate ASC
LIMIT 10;

-- 17. Century makers analysis
WITH batting_scores AS (
    SELECT 
        d.batter,
        d.match_id,
        d.innings_number,
        SUM(d.batter_runs) as runs_scored
    FROM deliveries d
    WHERE d.batter IS NOT NULL
    GROUP BY d.batter, d.match_id, d.innings_number
)
SELECT 
    batter,
    COUNT(*) as centuries,
    MAX(runs_scored) as highest_score,
    ROUND(AVG(runs_scored), 2) as avg_score
FROM batting_scores
WHERE runs_scored >= 100
GROUP BY batter
ORDER BY centuries DESC, highest_score DESC;

-- 18. Win/Loss patterns by venue
SELECT 
    venue,
    city,
    COUNT(*) as matches,
    COUNT(DISTINCT winner) as different_winners,
    winner as most_successful_team,
    COUNT(CASE WHEN winner = (
        SELECT winner 
        FROM matches m2 
        WHERE m2.venue = m1.venue AND winner IS NOT NULL
        GROUP BY winner 
        ORDER BY COUNT(*) DESC 
        LIMIT 1
    ) THEN 1 END) as wins_by_top_team
FROM matches m1
WHERE venue IS NOT NULL AND winner IS NOT NULL
GROUP BY venue, city
HAVING matches >= 2
ORDER BY matches DESC;

-- 19. Powerplay analysis (first 6 overs)
SELECT 
    m.format,
    COUNT(DISTINCT d.match_id) as matches,
    ROUND(AVG(CASE WHEN d.over_number < 6 THEN d.total_runs END), 2) as avg_powerplay_runs_per_ball,
    COUNT(CASE WHEN d.over_number < 6 AND d.wicket_type IS NOT NULL THEN 1 END) as powerplay_wickets,
    COUNT(CASE WHEN d.over_number < 6 AND d.batter_runs >= 4 THEN 1 END) as powerplay_boundaries
FROM deliveries d
JOIN matches m ON d.match_id = m.match_id
GROUP BY m.format
ORDER BY avg_powerplay_runs_per_ball DESC;

-- 20. Match outcome predictions based on first innings score
SELECT 
    m.format,
    CASE 
        WHEN i1.total_runs >= 300 THEN '300+'
        WHEN i1.total_runs >= 250 THEN '250-299'
        WHEN i1.total_runs >= 200 THEN '200-249'
        WHEN i1.total_runs >= 150 THEN '150-199'
        ELSE 'Below 150'
    END as first_innings_score_range,
    COUNT(*) as matches,
    SUM(CASE WHEN m.winner = i1.batting_team THEN 1 ELSE 0 END) as wins,
    ROUND(SUM(CASE WHEN m.winner = i1.batting_team THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as win_percentage
FROM matches m
JOIN innings i1 ON m.match_id = i1.match_id AND i1.innings_number = 1
WHERE m.winner IS NOT NULL
GROUP BY m.format, first_innings_score_range
ORDER BY m.format, first_innings_score_range;