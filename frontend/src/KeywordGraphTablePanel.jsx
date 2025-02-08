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
            <div className='flex flex-col items-center'>
                <div>
                    <KeywordInput keywords={keywords} setKeywords={setKeywords} />
                </div>
                <div className='mt-4'>
                    <span className="loading loading-spinner loading-lg text-gray-700"></span>
                </div>
            </div>
        )
    }

    return (

        <div className='flex flex-col items-center'>
            <div>
                <KeywordInput keywords={keywords} setKeywords={setKeywords} />
            </div>
            <div className='mt-4'>
                {isLoading && <span className="loading loading-spinner loading-md text-gray-700"></span>}
            </div>
            <div className="w-11/12">
                <Graph graphData={graphData} setSampleData={setSampleData} />
                {sampleData && <Table sampleData={sampleData} />}
            </div>
        </div>
    );
}

export default KeywordGraphTablePanel;