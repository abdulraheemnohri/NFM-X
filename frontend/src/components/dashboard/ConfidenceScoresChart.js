import React from 'react';
import { useTranslation } from 'react-i18next';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Paper } from '@mui/material';

function ConfidenceScoresChart({ data, height = 400 }) {
  const { t } = useTranslation();

  return (
    <Paper elevation={0} sx={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="range" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </Paper>
  );
}

export default ConfidenceScoresChart;

// Urdu: NFM-X Confidence Scores Chart
// یہ confidence scores ko bar chart ke zariye dikhane ke liye component ہے