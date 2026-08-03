import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from "react";
import { Card, Typography, List, Divider } from "antd";
const { Title, Text } = Typography;
const MemoryV2Page = () => {
    const [versions, setVersions] = React.useState([]);
    const [selectedVersion, setSelectedVersion] = React.useState(null);
    return (_jsxs("div", { style: { padding: 24 }, children: [_jsx(Title, { level: 2, children: "Memory V2 - Versioned Explorer" }), _jsx(Text, { type: "secondary", children: "Enhanced memory management with complete version history and rollback capability" }), _jsx(Divider, {}), _jsxs("div", { style: { display: "flex", gap: 24 }, children: [_jsx("div", { style: { flex: 1 }, children: _jsx(Card, { title: "Version History", children: _jsx(List, { dataSource: versions, renderItem: (item) => (_jsxs(List.Item, { onClick: () => setSelectedVersion(item), style: { cursor: "pointer" }, children: [_jsx(List.Item.Meta, { title: `Version ${item.version}`, description: item.createdAt }), _jsx("div", { children: item.tags.map(tag => (_jsxs("span", { style: { marginRight: 8 }, children: ["#", tag] }, tag))) })] })) }) }) }), _jsx("div", { style: { flex: 1 }, children: _jsx(Card, { title: "Version Content", children: selectedVersion ? (_jsxs("div", { children: [_jsxs(Title, { level: 4, children: ["Version ", selectedVersion.version] }), _jsxs(Text, { type: "secondary", children: ["Created: ", selectedVersion.createdAt] }), _jsx(Divider, {}), _jsx("pre", { style: { whiteSpace: "pre-wrap" }, children: selectedVersion.content })] })) : (_jsx(Text, { type: "secondary", children: "Select a version to view content" })) }) })] })] }));
};
export default MemoryV2Page;
