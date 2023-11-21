package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	"github.com/rs/cors"
)

// Constants for SQL queries to retrieve data from the database.
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

// KeywordSample represents a sample of a news headline including the headline text, its URL, and publication date.
type KeywordSample struct {
	Headline string `json:"headline" db:"headline"`
	WebUrl   string `json:"web_url" db:"web_url"`
	PubDate  string `json:"pub_date" db:"pub_date"`
}

// YearMonthOccurrence represents the number of headlines for a given year and month.
type YearMonthOccurrence struct {
	YearMonth    string `json:"x" db:"year_month"`
	NumHeadlines int    `json:"y" db:"num_headlines"`
}

// KeywordOccurrence holds the occurrences of a keyword in headlines over a series of months.
type KeywordOccurrence struct {
	Keyword     string                `json:"id"`
	Occurrences []YearMonthOccurrence `json:"data"`
}

var db *sqlx.DB

// initDB initializes the connection to the database and is called before the server starts.
func initDB() error {
	host := os.Getenv("db_host")
	user := os.Getenv("db_user")
	password := os.Getenv("db_password")
	dbName := os.Getenv("db_name")
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, "5432", user, password, dbName)

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

// getSample handles HTTP requests to retrieve a random sample of headlines for a given keyword and year/month.
func getSample(w http.ResponseWriter, r *http.Request) {

	keyword := r.URL.Query().Get("keyword")
	yearMonth := r.URL.Query().Get("year_month")
	if keyword == "" || yearMonth == "" {
		msg := "Missing 'keyword' or 'year_month' parameter"
		log.Println(msg)
		http.Error(w, msg, http.StatusBadRequest)
		return
	}

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

// getKeywordOccurences handles HTTP requests to retrieve the number of occurrences of each keyword by year and month.
func getKeywordOccurences(w http.ResponseWriter, r *http.Request) {

	queryKeywords := r.URL.Query().Get("keywords")
	if queryKeywords == "" {
		msg := "Missing 'keywords' parameter"
		log.Println(msg)
		http.Error(w, msg, http.StatusBadRequest)
		return
	}

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
		AllowedOrigins:   []string{"http://localhost:5173", "http://localhost", "https://news-headline-trends.vercel.app"},
		AllowCredentials: true,
		AllowedMethods:   []string{"GET"},
	})

	handler := c.Handler(mux)

	err = http.ListenAndServe(":8050", handler)
	if err != nil {
		log.Fatalf("failed to start server: %v", err)
	}
}
