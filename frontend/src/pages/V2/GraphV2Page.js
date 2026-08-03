import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from "react";
import { Card, Typography, Graph } from "antd";
const { Title, Text } = Typography;
const GraphV2Page = () => {
    const [nodes, setNodes] = React.useState([]);
    const [edges, setEdges] = React.useState([]);
    const graphData = {
        nodes,
        edges
    };
    const graphConfig = {
        nodeLabel: {
            style: {
                fill: "#000"
            }
        },
        edgeLabel: {
            style: {
                fill: "#666"
            }
        }
    };
    return (_jsxs("div", { style: { padding: 24 }, children: [_jsx(Title, { level: 2, children: "Memory Graph V2" }), _jsx(Text, { type: "secondary", children: "Interactive visualization of memory relationships and connections" }), _jsx(Card, { style: { marginTop: 24 }, children: _jsx(Graph, { data: graphData, config: graphConfig, style: { height: 600, width: "100%" } }) })] }));
};
export default GraphV2Page;
