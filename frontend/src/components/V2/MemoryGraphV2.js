import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Card, Typography } from "antd";
const { Title, Text } = Typography;
const MemoryGraphV2 = ({ memoryId, connections, depth }) => {
    return (_jsxs(Card, { style: { margin: 16 }, children: [_jsx(Title, { level: 4, children: "Memory Graph V2" }), _jsxs(Text, { children: ["ID: ", memoryId] }), _jsx("div", { style: { marginTop: 16 }, children: _jsxs(Text, { type: "secondary", children: ["Connections: ", connections] }) }), _jsx("div", { children: _jsxs(Text, { type: "secondary", children: ["Traversal Depth: ", depth] }) })] }));
};
export default MemoryGraphV2;
