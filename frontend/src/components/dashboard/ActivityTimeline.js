import React from 'react';
import { useTranslation } from 'react-i18next';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Paper } from '@mui/material';

function ActivityTimeline({ data, height = 400 }) {
  const { t } = useTranslation();

  return (
    <Paper elevation={0} sx={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="count" stroke="#8884d8" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
}

export default ActivityTimeline;

// Urdu: NFM-X Activity Timeline
// یہ activity timeline ko line chart ke zariye dikhane ke liye component hai