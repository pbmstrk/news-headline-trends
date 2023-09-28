import { useState, useEffect } from 'react'

function Table({ sampleData }) {
    const [tableData, setTableData] = useState(null);

    useEffect(() => {
        if (sampleData) {
            fetch(`http://127.0.0.1:8000/samples?keyword=${sampleData.keyword}&year_month=${sampleData.year_month}`)
                .then(response => response.json())
                .then(data => {
                    setTableData(data);
                })
                .catch(error => {
                    console.error("There was an error fetching table data:", error);
                });
        }
    }, [sampleData]);

    if (!tableData) {
        return (
            <div className="mt-8 flex justify-center">
                <span className="loading loading-spinner loading-lg"></span>
            </div>
        )
    }

    return (
        <div className="overflow-x-auto">
            <table className='table'>
                <thead>
                    <tr>
                        <th>Headline</th>
                        <th>Publication Date</th>
                    </tr>
                </thead>
                <tbody>
                    {tableData.map((item, index) => (
                        <tr key={index}>
                            <td><a
                                className='text-blue-700'
                                href={item.web_url}
                                rel="noopener noreferrer"
                                target='_blank'>{item.headline}
                                </a></td>
                            <td>{item.pub_date}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Table;