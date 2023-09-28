import { ResponsiveLine } from '@nivo/line';
import { useWindowSize } from 'react-use';

const CustomTooltip = ({ point }) => {
    const data = point.data;

    return (
        <div style={{ background: 'white', padding: '10px', border: '1px solid #ccc' }}>
            <strong>{point.serieId}</strong><br />
            <strong>Month:</strong> {data.x.toLocaleDateString()}<br />
            <strong>Number of occurences:</strong> {data.y}
        </div>
    );
};

function formatDate(date) {
    var year = date.toLocaleString("default", { year: "numeric" });
    var month = date.toLocaleString("default", { month: "2-digit" });

    return year + "-" + month
}



function Graph({ graphData, setSampleData }) {

    const { width } = useWindowSize();

    let tickInterval;
    if (width <= 500) {
        tickInterval = "every 6 years";
    } else if (width <= 800) {
        tickInterval = "every 4 years";
    } else {
        tickInterval = "every 2 years";
    }

    const handlePointClick = (point, _) => {
        console.log(point);
        setSampleData({ keyword: point.serieId, year_month: formatDate(point.data.x) });
    };

    return (
        <div style={{ height: 400 }}>
            <ResponsiveLine
                data={graphData}
                margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
                xScale={{ type: "time", format: "%Y-%m" }}
                yScale={{ type: 'linear', min: 'auto', max: 'auto', stacked: false, reverse: false }}
                axisTop={null}
                axisRight={null}
                curve="cardinal"
                axisBottom={{
                    format: "%b %Y",
                    tickValues: tickInterval,
                    legend: "Month",
                    legendPosition: "middle",
                    legendOffset: 40
                }}
                axisLeft={{
                    orient: 'left',
                    tickSize: 5,
                    tickPadding: 5,
                    tickRotation: 0,
                    legend: 'Number of headlines',
                    legendOffset: -40,
                    legendPosition: 'middle'
                }}
                colors={{ scheme: 'category10' }}
                pointColor={{ from: 'color', modifiers: [] }}
                pointSize={3}
                onClick={handlePointClick}
                pointBorderWidth={1}
                pointBorderColor={{ from: 'color', modifiers: [] }}
                useMesh={true}
                enableCrosshair={false}
                tooltip={CustomTooltip}
                legends={[
                    {
                        anchor: 'bottom-right',
                        direction: 'column',
                        justify: false,
                        translateX: 100,
                        translateY: 0,
                        itemsSpacing: 0,
                        itemDirection: 'left-to-right',
                        itemWidth: 80,
                        itemHeight: 20,
                        itemOpacity: 0.75,
                        symbolSize: 12,
                        symbolShape: 'circle',
                        symbolBorderColor: 'rgba(0, 0, 0, .5)',
                        effects: [
                            {
                                on: 'hover',
                                style: {
                                    itemBackground: 'rgba(0, 0, 0, .03)',
                                    itemOpacity: 1
                                }
                            }
                        ]
                    }
                ]}
            />
        </div>

    );
}

export default Graph;