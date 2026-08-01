import React from 'react';
import { useTranslation } from 'react-i18next';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Paper } from '@mui/material';

function TopTagsChart({ data, height = 400 }) {
  const { t } = useTranslation();

  return (
    <Paper elevation={0} sx={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="tag" type="category" width={150} />
          <Tooltip />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </Paper>
  );
}

export default TopTagsChart;

// Urdu: NFM-X Top Tags Chart
// یہ top tags ko horizontal bar chart ke zariye dikhane ke liye component ہے