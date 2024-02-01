import { useState, useEffect } from 'react'
import Table from './Table'
import Graph from './Graph'
import KeywordInput from './KeywordInput'

function KeywordGraphTablePanel() {
    const [keywords, setKeywords] = useState(['trump', 'obama']);
    const [graphData, setGraphData] = useState(null);
    const [sampleData, setSampleData] = useState(null);
    const [isLoading, setIsLoading] = useState(false); 

    let apiURL = import.meta.env.VITE_API_URL;

    const fetchData = (keywordsToFetch) => {
        setIsLoading(true);       
        fetch(`${apiURL}/occurrences?keywords=${keywordsToFetch.join(",")}`)
            .then(response => response.json())
            .then(data => {
                setGraphData(data);
            })
            .catch(error => {
                console.error("There was an error fetching graph data:", error);
            })
            .finally(() => {
                setIsLoading(false); 
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
                    <span className="loading loading-spinner loading-lg text-gray-700"></span>
                </div>
            </div>
        )
    }


    return (
        <div className="flex flex-col">
            <div className="flex items-center">
                <KeywordInput keywords={keywords} setKeywords={setKeywords} />
                {isLoading && <span className="loading loading-spinner loading-md ml-2 text-gray-700"></span>}
            </div>
            <Graph graphData={graphData} setSampleData={setSampleData} />
            {sampleData && <Table sampleData={sampleData} />}
        </div>
    );
}

export default KeywordGraphTablePanel;