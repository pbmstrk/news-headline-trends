package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"strings"
	"time"

	"github.com/rs/cors"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

const SAMPLE_HEADLINES_QUERY = `
select 
    headline, web_url,
    to_char(cast(pub_date as timestamp), 'yyyy-mm-dd') as pub_date
from headlines
where textsearchable_index_col @@ to_tsquery('simple', ?) and year_month = ?;
`
const KEYWORD_OCCURRENCE_QUERY = `
select 
	year_month,
	count(headline) as num_headlines
from headlines
where textsearchable_index_col @@ to_tsquery('simple', ?)
group by year_month
order by year_month;
`

type KeywordSample struct {
	Headline string `json:"headline"`
	PubDate  string `json:"pub_date"`
}

type YearMonthOccurrence struct {
	YearMonth    string `json:"x"`
	NumHeadlines int    `json:"y"`
}

type KeywordOccurrence struct {
	Keyword     string                `json:"id"`
	Occurrences []YearMonthOccurrence `json:"data"`
}

func getDB() *gorm.DB {
	host := "localhost"
	user := "postgres"
	password := "postgres"
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, "5432", user, password, "nytdata_clj")
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal(err)
	}
	return db
}

func getSample(w http.ResponseWriter, r *http.Request) {
	db := getDB()

	dbInstance, _ := db.DB()
	defer dbInstance.Close()

	keyword := r.URL.Query().Get("keyword")
	yearMonth := r.URL.Query().Get("year_month")

	samples := []KeywordSample{}
	db.Raw(SAMPLE_HEADLINES_QUERY, keyword, yearMonth).Scan(&samples)

	rand.Shuffle(len(samples), func(i, j int) {
		samples[i], samples[j] = samples[j], samples[i]
	})

	sampleSize := min(5, len(samples))
	sample := samples[:sampleSize]

	jsonData, err := json.Marshal(sample)
	if err != nil {
		log.Fatal(err)
	}
	w.Header().Set("Content-Type", "application/json")
	w.Write(jsonData)
}

func padDates(occurrences []YearMonthOccurrence) []YearMonthOccurrence {
	paddedOccurrences := []YearMonthOccurrence{}
	if len(occurrences) == 0 {
		return paddedOccurrences
	}

	prevMonth, err := time.Parse("2006-01", occurrences[0].YearMonth)
	if err != nil {
		log.Fatal(err)
	}

	paddedOccurrences = append(paddedOccurrences, occurrences[0])

	for i := 1; i < len(occurrences); i++ {
		curMonth, err := time.Parse("2006-01", occurrences[i].YearMonth)
		if err != nil {
			log.Fatal(err)
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

	return paddedOccurrences
}

func getKeywordOccurences(w http.ResponseWriter, r *http.Request) {
	db := getDB()

	dbInstance, _ := db.DB()
	defer dbInstance.Close()

	queryKeywords := r.URL.Query().Get("keywords")
	keywords := strings.Split(queryKeywords, ",")
	var occurrences []KeywordOccurrence

	for _, keyword := range keywords {
		var dbResults []YearMonthOccurrence
		db.Raw(KEYWORD_OCCURRENCE_QUERY, keyword).Scan(&dbResults)
		occurrences = append(occurrences, KeywordOccurrence{
			Keyword:     keyword,
			Occurrences: padDates(dbResults),
		})
	}

	jsonData, err := json.Marshal(occurrences)
	if err != nil {
		log.Fatal(err)
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(jsonData)
}

func main() {
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
