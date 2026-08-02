import React, { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { Layout as AntLayout, Menu, Button, Avatar, Dropdown, Space } from "antd";
import { MenuFoldOutlined, MenuUnfoldOutlined, HomeOutlined, FileTextOutlined, SearchOutlined, DatabaseOutlined, SettingOutlined, BarChartOutlined, FileAddOutlined, UploadOutlined, CloudOutlined } from "@ant-design/icons";

const { Header, Sider, Content } = AntLayout;

const ModernLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  const menuItems = [
    { key: "/", icon: <HomeOutlined />, label: <Link to="/">Dashboard</Link> },
    { key: "/memories", icon: <FileTextOutlined />, label: <Link to="/memories">Memories</Link> },
    { key: "/search", icon: <SearchOutlined />, label: <Link to="/search">Search</Link> },
    { key: "/graph", icon: <DatabaseOutlined />, label: <Link to="/graph">Graph</Link> },
    { key: "/v2", icon: <CloudOutlined />, label: "V2 Features", children: [
      { key: "/v2/memory", icon: <FileTextOutlined />, label: <Link to="/v2/memory">Memory V2</Link> },
      { key: "/v2/graph", icon: <DatabaseOutlined />, label: <Link to="/v2/graph">Graph V2</Link> },
      { key: "/v2/conflicts", icon: <SettingOutlined />, label: <Link to="/v2/conflicts">Conflicts V2</Link> },
    ]},
    { key: "/documents", icon: <FileAddOutlined />, label: <Link to="/documents">Documents</Link> },
    { key: "/upload", icon: <UploadOutlined />, label: <Link to="/upload">Upload</Link> },
    { key: "/settings", icon: <SettingOutlined />, label: <Link to="/settings">Settings</Link> },
    { key: "/stats", icon: <BarChartOutlined />, label: <Link to="/stats">Statistics</Link> },
  ];

  return (
    <AntLayout style={{ minHeight: "100vh" }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={(value) => setCollapsed(value)}
        width={256}
        className="shadow-xl bg-gray-900"
      >
        <div className="flex items-center justify-center h-16 px-4 py-4 border-b border-gray-800">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">N</span>
            </div>
            {!collapsed && <span className="text-white font-bold text-xl">NFM-X</span>}
          </div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems as any}
          className="bg-gray-900 border-gray-800"
        />
      </Sider>
      <AntLayout>
        <Header className="bg-white px-6 py-3 shadow-sm border-b border-gray-200 flex items-center justify-between">
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            className="text-gray-600"
          />
          <Dropdown
            menu={{
              items: [
                { key: "profile", label: "Profile" },
                { key: "settings", label: "Settings" },
                { type: "divider" },
                { key: "logout", label: "Logout", danger: true },
              ],
            }}
            trigger={["click"]}
          >
            <Button type="text" className="flex items-center space-x-2">
              <Avatar size="small" className="bg-indigo-500">AN</Avatar>
              {!collapsed && <span>Abdulraheem</span>}
            </Button>
          </Dropdown>
        </Header>
        <Content className="m-6">
          <div className="p-6 min-h-[calc(100vh-120px)] bg-white rounded-xl shadow-sm border border-gray-200">
            <Outlet />
          </div>
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default ModernLayout;