package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"strings"
	"time"

	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	"github.com/rs/cors"
)

const sampleHeadlinesQuery = `
select 
    headline, web_url,
    to_char(cast(pub_date as timestamp), 'yyyy-mm-dd') as pub_date
from headlines
where textsearchable_index_col @@ to_tsquery('simple', $1) and year_month = $2;
`
const keyOccurrenceQuery = `
select 
	year_month,
	count(headline) as num_headlines
from headlines
where textsearchable_index_col @@ to_tsquery('simple', $1)
group by year_month
order by year_month;
`

type KeywordSample struct {
	Headline string `json:"headline" db:"headline"`
	WebUrl   string `json:"web_url" db:"web_url"`
	PubDate  string `json:"pub_date" db:"pub_date"`
}

type YearMonthOccurrence struct {
	YearMonth    string `json:"x" db:"year_month"`
	NumHeadlines int    `json:"y" db:"num_headlines"`
}

type KeywordOccurrence struct {
	Keyword     string                `json:"id"`
	Occurrences []YearMonthOccurrence `json:"data"`
}

var db *sqlx.DB

func initDB() error {
	host := "localhost"
	user := "postgres"
	password := "postgres"
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, "5432", user, password, "nytdata_clj")

	var err error
	db, err = sqlx.Open("postgres", dsn)
	if err != nil {
		return fmt.Errorf("error opening database: %w", err)
	}
	return nil
}

func handleError(w http.ResponseWriter, err error, statusCode int) {
	log.Printf("error: %v", err)
	http.Error(w, http.StatusText(statusCode), statusCode)
}

func getSample(w http.ResponseWriter, r *http.Request) {

	keyword := r.URL.Query().Get("keyword")
	yearMonth := r.URL.Query().Get("year_month")

	samples := []KeywordSample{}
	err := db.Select(&samples, sampleHeadlinesQuery, keyword, yearMonth)
	if err != nil {
		handleError(w, err, http.StatusInternalServerError)
		return
	}

	rand.Shuffle(len(samples), func(i, j int) {
		samples[i], samples[j] = samples[j], samples[i]
	})

	sampleSize := min(5, len(samples))
	sample := samples[:sampleSize]

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(sample)
}

func padDates(occurrences []YearMonthOccurrence) ([]YearMonthOccurrence, error) {
	paddedOccurrences := []YearMonthOccurrence{}
	if len(occurrences) == 0 {
		return paddedOccurrences, nil
	}

	prevMonth, err := time.Parse("2006-01", occurrences[0].YearMonth)
	if err != nil {
		return nil, fmt.Errorf("error parsing date: %w", err)
	}

	paddedOccurrences = append(paddedOccurrences, occurrences[0])

	for i := 1; i < len(occurrences); i++ {
		curMonth, err := time.Parse("2006-01", occurrences[i].YearMonth)
		if err != nil {
			return nil, fmt.Errorf("error parsing date: %w", err)
		}

		monthDiff := int(curMonth.Sub(prevMonth).Hours() / 24 / 30)
		if monthDiff > 1 {
			for j := 1; j < monthDiff; j++ {
				gapMonth := prevMonth.AddDate(0, j, 0)
				paddedOccurrences = append(paddedOccurrences, YearMonthOccurrence{
					YearMonth:    gapMonth.Format("2006-01"),
					NumHeadlines: 0,
				})
			}
		}

		paddedOccurrences = append(paddedOccurrences, occurrences[i])
		prevMonth = curMonth
	}

	return paddedOccurrences, nil
}

func getKeywordOccurences(w http.ResponseWriter, r *http.Request) {

	queryKeywords := r.URL.Query().Get("keywords")
	keywords := strings.Split(queryKeywords, ",")
	var occurrences []KeywordOccurrence

	for _, keyword := range keywords {
		var dbResults []YearMonthOccurrence
		err := db.Select(&dbResults, keyOccurrenceQuery, keyword)
		if err != nil {
			handleError(w, err, http.StatusInternalServerError)
			return
		}
		paddedDbResults, err := padDates(dbResults)
		if err != nil {
			handleError(w, err, http.StatusInternalServerError)
			return
		}

		occurrences = append(occurrences, KeywordOccurrence{
			Keyword:     keyword,
			Occurrences: paddedDbResults,
		})
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(occurrences)
}

func main() {

	// Initialize the database connection pool
	err := initDB()
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	mux := http.NewServeMux()
	mux.HandleFunc("/samples", getSample)
	mux.HandleFunc("/occurrences", getKeywordOccurences)

	c := cors.New(cors.Options{
		AllowedOrigins:   []string{"http://localhost:5173", "https://news-headline-trends.vercel.app"},
		AllowCredentials: true,
		AllowedMethods:   []string{"GET"},
	})

	handler := c.Handler(mux)

	http.ListenAndServe(":3333", handler)
}
