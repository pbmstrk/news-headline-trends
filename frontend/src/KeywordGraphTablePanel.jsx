import { useState, useEffect } from 'react'
import Table from './Table'
import Graph from './Graph'
import KeywordInput from './KeywordInput'

function KeywordGraphTablePanel() {
    const [keywords, setKeywords] = useState(['trump', 'obama']);
    const [graphData, setGraphData] = useState(null);
    const [sampleData, setSampleData] = useState(null);

    let apiURL = import.meta.env.VITE_API_URL;

    const fetchData = (keywordsToFetch) => {
        fetch(`${apiURL}/occurrences?keywords=${keywordsToFetch.join(",")}`)
            .then(response => response.json())
            .then(data => {
                setGraphData(data);
            })
            .catch(error => {
                console.error("There was an error fetching graph data:", error);
            });
    };

    useEffect(() => {
        // don't fetch data if keyword list is empty. This'll keep the graph populated 
        // with the last present keyword.
        if (keywords.length >= 1) {
            fetchData(keywords);
        }
    }, [keywords]);

    if (!graphData) {
        return (
            <div className="flex flex-col">
                <KeywordInput keywords={keywords} setKeywords={setKeywords} />
                <div className="mt-8 flex justify-center">
                    <span className="loading loading-spinner loading-lg"></span>
                </div>
            </div>
        )
    }


    return (
        <div>
            <KeywordInput keywords={keywords} setKeywords={setKeywords} />
            <Graph graphData={graphData} setSampleData={setSampleData} />
            {sampleData && <Table sampleData={sampleData} />}
        </div>
    );
}

export default KeywordGraphTablePanel;