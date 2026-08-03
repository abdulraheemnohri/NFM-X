import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from "react";
import { Card, Typography, Button, Steps, Divider } from "antd";
const { Title, Text } = Typography;
const ConflictResolverV2 = ({ conflictId, conflictType, severity, onResolve }) => {
    const [currentStep, setCurrentStep] = React.useState(0);
    const steps = [
        {
            title: "Detect",
            description: "Analyzing conflict..."
        },
        {
            title: "Analyze",
            description: "Understanding conflict type..."
        },
        {
            title: "Resolve",
            description: "Applying resolution strategy..."
        }
    ];
    const resolutionStrategies = [
        { name: "Merge", description: "Combine conflicting memories" },
        { name: "Prioritize", description: "Keep the most recent version" },
        { name: "Archive", description: "Archive old versions" },
        { name: "Manual", description: "Mark for manual review" }
    ];
    return (_jsxs(Card, { style: { margin: 16 }, children: [_jsx(Title, { level: 4, children: "Conflict Resolver V2" }), _jsxs(Text, { type: "secondary", children: ["ID: ", conflictId] }), _jsx(Divider, {}), _jsx(Steps, { current: currentStep, items: steps }), _jsx(Divider, {}), _jsxs(Title, { level: 5, children: ["Type: ", conflictType] }), _jsxs(Text, { type: "secondary", children: ["Severity: ", severity] }), _jsx(Divider, {}), _jsx(Title, { level: 5, children: "Resolution Strategies" }), _jsx("div", { style: { display: "flex", flexWrap: "wrap", gap: 8 }, children: resolutionStrategies.map(strategy => (_jsx(Button, { type: "primary", onClick: () => {
                        onResolve(strategy.name);
                        setCurrentStep(2);
                    }, children: strategy.name }, strategy.name))) })] }));
};
export default ConflictResolverV2;
