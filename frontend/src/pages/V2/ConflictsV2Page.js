import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from "react";
import { Card, Typography, Table, Button, Tag } from "antd";
const { Title, Text } = Typography;
const ConflictsV2Page = () => {
    const [conflicts, setConflicts] = React.useState([]);
    const columns = [
        {
            title: "ID",
            dataIndex: "id",
            key: "id"
        },
        {
            title: "Type",
            dataIndex: "type",
            key: "type"
        },
        {
            title: "Severity",
            dataIndex: "severity",
            key: "severity",
            render: (severity) => {
                let color = "default";
                if (severity === "high" || severity === "critical")
                    color = "red";
                else if (severity === "medium")
                    color = "orange";
                else if (severity === "low")
                    color = "green";
                return _jsx(Tag, { color: color, children: severity });
            }
        },
        {
            title: "Status",
            dataIndex: "status",
            key: "status",
            render: (status) => {
                let color = "default";
                if (status === "resolved")
                    color = "green";
                else if (status === "resolving")
                    color = "blue";
                else if (status === "detected")
                    color = "orange";
                return _jsx(Tag, { color: color, children: status });
            }
        },
        {
            title: "Memories",
            dataIndex: "memoryIds",
            key: "memoryIds",
            render: (ids) => ids.join(", ")
        },
        {
            title: "Actions",
            key: "actions",
            render: (_, record) => (_jsx(Button, { type: "primary", size: "small", children: "Auto-Resolve" }))
        }
    ];
    return (_jsxs("div", { style: { padding: 24 }, children: [_jsx(Title, { level: 2, children: "Conflicts V2 - AI Auto-Resolution" }), _jsx(Text, { type: "secondary", children: "Advanced conflict detection and automatic resolution" }), _jsxs(Card, { style: { marginTop: 24 }, children: [_jsx(Button, { type: "primary", style: { marginBottom: 16 }, children: "Detect All Conflicts" }), _jsx(Button, { style: { marginLeft: 8, marginBottom: 16 }, children: "Auto-Resolve All" }), _jsx(Table, { columns: columns, dataSource: conflicts, rowKey: "id" })] })] }));
};
export default ConflictsV2Page;
