import React from 'react';
import { useTranslation } from 'react-i18next';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Paper } from '@mui/material';

const COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
  '#FFEAA7', '#DDDDDD', '#2ECC71', '#9B59B6',
  '#3498DB', '#F39C12', '#E74C3C', '#1ABC9C'
];

function MemoryTypeChart({ memoryTypes, height = 400 }) {
  const { t } = useTranslation();

  const chartData = memoryTypes.map((item, index) => ({
    name: t('memory_type_' + item.type.toLowerCase()),
    value: item.count,
    fill: COLORS[index % COLORS.length]
  }));

  return (
    <Paper elevation={0} sx={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => name + ': ' + (percent * 100).toFixed(0) + '%'}
          >
            {chartData.map((entry, index) => (
              <Cell key={'cell-' + index} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value, name, props) => [
              value + ' memories',
              name,
              (props.payload.percent * 100).toFixed(1) + '%'
            ]}
          />
          <Legend 
            layout="vertical" 
            align="right" 
            verticalAlign="middle"
            wrapperStyle={{ paddingLeft: '20px' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </Paper>
  );
}

export default MemoryTypeChart;

// Urdu: NFM-X Memory Type Chart
// یہ memory types کی distribution ko pie chart ke zariye dikhane ke liye component ہے