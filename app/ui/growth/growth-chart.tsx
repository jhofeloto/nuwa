'use client';
import { ResponsiveLine } from '@nivo/line';
import { useTheme } from 'next-themes';

import { LineChartProps } from '@/app/lib/definitions';
import { useMediaQuery } from 'react-responsive';

const CustomTooltip = ({ value }: { value: number }) => {
  const { theme } = useTheme();
  const labelBackgroundColor = theme === 'dark' ? '#333' : '#fff';
  const textColor = theme === 'dark' ? '#fff' : '#000';

  return (
    <div style={{ backgroundColor: labelBackgroundColor, color: textColor, padding: '5px', borderRadius: '3px' }}>
      {value}
    </div>
  );
};

const GrowthChart: React.FC<LineChartProps> = ({ data }) => {
  const isMobile = useMediaQuery({ maxWidth: 767 });
  const isTablet = useMediaQuery({ minWidth: 768, maxWidth: 1024 });
  const { theme } = useTheme();
  const textColor = theme === 'dark' ? '#fff' : '#000';

  if (!data || data.length === 0) {
    return <p className="text-center text-gray-500">Please choose your options and press submit</p>;
  }

  return (
      <div style={{ height: isMobile ? '300px' : '500px', width: '100%' }}>
        <ResponsiveLine
          data={data}
          margin={{ top: isMobile ? 100 : 50, right: isMobile ? 10 : 150, bottom: isMobile ? 100 : 50, left: 60 }}
          xScale={{ type: 'point' }}
          yScale={{
            type: 'linear',
            min: 'auto',
            max: 'auto',
            stacked: false,
            reverse: false,
          }}
          yFormat={function (y) { return typeof y === 'number' ? y.toPrecision(4) : String(y); }}
          axisTop={null}
          axisRight={null}
          axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'year',
            legendOffset: 36,
            legendPosition: 'middle',
            tickValues: 5,
          }}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Co2eq (Kg)',
            legendOffset: -55,
            legendPosition: 'middle',
            tickValues: 5,
          }}
          colors={{ scheme: 'nivo' }}
          pointSize= {isMobile ? 2 : 10}
          pointColor={{ theme: 'background' }}
          pointBorderWidth={2}
          pointBorderColor={{ from: 'serieColor' }}
          pointLabelYOffset={-12}
          useMesh={true}
          legends={[
            {
              anchor: isMobile ? 'top' : 'right',
              direction: isMobile ? 'row' : 'column',
              justify: false,
              translateX: isMobile ? 0 : 100,
              translateY: isMobile ? -50 : 0,
              itemsSpacing: isMobile ? 2 : 0,
              itemDirection: 'left-to-right',
              itemWidth: 80,
              itemHeight: 20,
              itemOpacity: 0.85,
              symbolSize: 12,
              symbolShape: 'circle',
              symbolBorderColor: textColor,
              effects: [
                {
                  on: 'hover',
                  style: {
                    itemOpacity: 1,
                  },
                },
              ],
              itemTextColor: textColor,
            },
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
                    fontSize: isMobile ? 8 : isTablet ? 10 : 10,
                    fill: textColor // Set legend text color based on mode
                }
            }
        }}
        tooltip={({ point }) => <CustomTooltip value={point.data.y as number} />}
        />
      </div>
  );
};

export default GrowthChart;
