import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { Layout as AntLayout, Menu, Button, Avatar, Dropdown } from "antd";
import { MenuFoldOutlined, MenuUnfoldOutlined, HomeOutlined, FileTextOutlined, SearchOutlined, DatabaseOutlined, SettingOutlined, BarChartOutlined, FileAddOutlined, UploadOutlined, CloudOutlined } from "@ant-design/icons";
const { Header, Sider, Content } = AntLayout;
const ModernLayout = () => {
    const [collapsed, setCollapsed] = useState(false);
    const location = useLocation();
    const menuItems = [
        { key: "/", icon: _jsx(HomeOutlined, {}), label: _jsx(Link, { to: "/", children: "Dashboard" }) },
        { key: "/memories", icon: _jsx(FileTextOutlined, {}), label: _jsx(Link, { to: "/memories", children: "Memories" }) },
        { key: "/search", icon: _jsx(SearchOutlined, {}), label: _jsx(Link, { to: "/search", children: "Search" }) },
        { key: "/graph", icon: _jsx(DatabaseOutlined, {}), label: _jsx(Link, { to: "/graph", children: "Graph" }) },
        { key: "/v2", icon: _jsx(CloudOutlined, {}), label: "V2 Features", children: [
                { key: "/v2/memory", icon: _jsx(FileTextOutlined, {}), label: _jsx(Link, { to: "/v2/memory", children: "Memory V2" }) },
                { key: "/v2/graph", icon: _jsx(DatabaseOutlined, {}), label: _jsx(Link, { to: "/v2/graph", children: "Graph V2" }) },
                { key: "/v2/conflicts", icon: _jsx(SettingOutlined, {}), label: _jsx(Link, { to: "/v2/conflicts", children: "Conflicts V2" }) },
            ] },
        { key: "/documents", icon: _jsx(FileAddOutlined, {}), label: _jsx(Link, { to: "/documents", children: "Documents" }) },
        { key: "/upload", icon: _jsx(UploadOutlined, {}), label: _jsx(Link, { to: "/upload", children: "Upload" }) },
        { key: "/settings", icon: _jsx(SettingOutlined, {}), label: _jsx(Link, { to: "/settings", children: "Settings" }) },
        { key: "/stats", icon: _jsx(BarChartOutlined, {}), label: _jsx(Link, { to: "/stats", children: "Statistics" }) },
    ];
    return (_jsxs(AntLayout, { style: { minHeight: "100vh" }, children: [_jsxs(Sider, { collapsible: true, collapsed: collapsed, onCollapse: (value) => setCollapsed(value), width: 256, className: "shadow-xl bg-gray-900", children: [_jsx("div", { className: "flex items-center justify-center h-16 px-4 py-4 border-b border-gray-800", children: _jsxs("div", { className: "flex items-center space-x-2", children: [_jsx("div", { className: "w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center", children: _jsx("span", { className: "text-white font-bold text-lg", children: "N" }) }), !collapsed && _jsx("span", { className: "text-white font-bold text-xl", children: "NFM-X" })] }) }), _jsx(Menu, { theme: "dark", mode: "inline", selectedKeys: [location.pathname], items: menuItems, className: "bg-gray-900 border-gray-800" })] }), _jsxs(AntLayout, { children: [_jsxs(Header, { className: "bg-white px-6 py-3 shadow-sm border-b border-gray-200 flex items-center justify-between", children: [_jsx(Button, { type: "text", icon: collapsed ? _jsx(MenuUnfoldOutlined, {}) : _jsx(MenuFoldOutlined, {}), onClick: () => setCollapsed(!collapsed), className: "text-gray-600" }), _jsx(Dropdown, { menu: {
                                    items: [
                                        { key: "profile", label: "Profile" },
                                        { key: "settings", label: "Settings" },
                                        { type: "divider" },
                                        { key: "logout", label: "Logout", danger: true },
                                    ],
                                }, trigger: ["click"], children: _jsxs(Button, { type: "text", className: "flex items-center space-x-2", children: [_jsx(Avatar, { size: "small", className: "bg-indigo-500", children: "AN" }), !collapsed && _jsx("span", { children: "Abdulraheem" })] }) })] }), _jsx(Content, { className: "m-6", children: _jsx("div", { className: "p-6 min-h-[calc(100vh-120px)] bg-white rounded-xl shadow-sm border border-gray-200", children: _jsx(Outlet, {}) }) })] })] }));
};
export default ModernLayout;
