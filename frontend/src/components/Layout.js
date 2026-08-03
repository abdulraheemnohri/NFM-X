import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Layout as AntLayout, Typography } from "antd";
import { Outlet } from "react-router-dom";
const { Header, Sider, Content } = AntLayout;
const { Title } = Typography;
export default function Layout() { return _jsxs(AntLayout, { children: [_jsx(Sider, { children: _jsx(Title, { level: 4, children: "NFM-X" }) }), _jsxs(AntLayout, { children: [_jsx(Header, { children: "Header" }), _jsx(Content, { children: _jsx(Outlet, {}) })] })] }); }
