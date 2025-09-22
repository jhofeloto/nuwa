'use client';
import { ResponsiveBar } from '@nivo/bar';
import { BarDatum } from '@nivo/bar';
import { useTheme } from 'next-themes';
import { useMediaQuery } from 'react-responsive';

interface MyResponsiveBarProps {
    data: BarDatum[];
}

function formatNumber(value: number): string {
  if (value >= 1e6) {
    return (value / 1e6).toFixed(1) + 'M';
  } else if (value >= 1e3) {
    return (value / 1e3).toFixed(1) + 'K';
  } else {
    return value.toString();
  }
}

const CustomTooltip = ({ value }: { value: number }) => {
  const { theme } = useTheme();
  const labelBackgroundColor = theme === 'dark' ? '#333' : '#fff';
  const textColor = theme === 'dark' ? '#fff' : '#000';

  return (
    <div style={{ backgroundColor: labelBackgroundColor, color: textColor, padding: '5px', borderRadius: '3px' }}>
      {formatNumber(value)}
    </div>
  );
};

const BarChartAggregated = ({ data }: MyResponsiveBarProps) => {
  const isMobile = useMediaQuery({ maxWidth: 767 });
  const isTablet = useMediaQuery({ minWidth: 768, maxWidth: 1024 });
  const { theme } = useTheme();

  const textColor = theme === 'dark' ? '#fff' : '#000';

  return (
    <div style={{ height: isMobile ? '300px' : '500px', width: '100%' }}> {/* Adjust height and width for mobile view */}
        <ResponsiveBar
            data={data}
            keys={[
                'bgb',
                'co2',
                'agb',
                'soc'
            ]}
            indexBy="ecosystem"
            margin={{ top: 50, right: 30, bottom: isMobile ? 100 : 50, left: 60 }} // Adjusted bottom margin for mobile view
            padding={0.3}
            groupMode="grouped"
            valueScale={{ type: 'linear' }}
            indexScale={{ type: 'band', round: true }}
            colors={{ scheme: 'nivo' }}
            borderColor={{
                from: 'color',
                modifiers: [
                    [
                        'darker',
                        1.6
                    ]
                ]
            }}
            axisTop={null}
            axisRight={null}
            axisLeft={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: 'Tonnes',
                legendPosition: 'middle',
                legendOffset: -50,
                format: (value) => formatNumber(value as number)
            }}
            axisBottom={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: isMobile ? 45 : 0,
                legend: 'Ecosystem',
                legendPosition: 'middle',
                legendOffset: 32,
                truncateTickAt: 0
            }}
            labelSkipWidth={12}
            labelSkipHeight={12}
            labelTextColor={{
                from: 'color',
                modifiers: [
                    [
                        'darker',
                        1.6
                    ]
                ]
            }}
            tooltip={({ value }) => <CustomTooltip value={value as number} />}
            label={(d) => formatNumber(d.value as number)}
            legends={[
                {
                    dataFrom: 'keys',
                    anchor: 'top',
                    direction: 'row',
                    justify: false,
                    translateX: 0,
                    translateY: isMobile ? -50 : -30,
                    itemsSpacing: 2,
                    itemWidth: isMobile ? 60 : 100,
                    itemHeight: 20,
                    itemDirection: isMobile ? 'top-to-bottom' : 'left-to-right',
                    itemOpacity: 0.85,
                    symbolSize: isMobile ? 10 : 20,
                    effects: [
                        {
                            on: 'hover',
                            style: {
                                itemOpacity: 1
                            }
                        }
                    ]
                }
            ]}
            theme={{
                labels: {
                    text: {
                        fontSize: isMobile ? 8 : isTablet ? 10 : 10,
                        fill: textColor // Set label text color based on mode
                    },
                },
                axis: {
                    ticks: {
                        text: {
                            fontSize: isMobile ? 8 : isTablet ? 10 : 10,
                            fill: textColor // Set axis tick text color based on mode
                        },
                    },
                    legend: {
                        text: {
                            fill: textColor // Set axis legend text color based on mode
                        }
                    }
                },
                legends: {
                    text: {
                        fill: textColor // Set legend text color based on mode
                    }
                }
            }}
        />
    </div>
  );
};

export default BarChartAggregated;