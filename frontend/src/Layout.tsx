import React, { useState } from 'react';
import { Layout as AntLayout, Menu, Button, theme, Avatar } from 'antd';
import {
  HomeOutlined,
  DatabaseOutlined,
  BarChartOutlined,
  AlertOutlined,
  ProjectOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const { Header, Sider, Content } = AntLayout;

interface LayoutProps {
  children: React.ReactNode;
}

function Layout({ children }: LayoutProps) {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">Home</Link>,
    },
    {
      key: '/memories',
      icon: <DatabaseOutlined />,
      label: <Link to="/memories">Memories</Link>,
    },
    {
      key: '/stats',
      icon: <BarChartOutlined />,
      label: <Link to="/stats">Statistics</Link>,
    },
    {
      key: '/conflicts',
      icon: <AlertOutlined />,
      label: <Link to="/conflicts">Conflicts</Link>,
    },
    {
      key: '/graph',
      icon: <ProjectOutlined />,
      label: <Link to="/graph">Graph</Link>,
    },
  ];

  const selectedKey = location.pathname.split('/')[1] || '/';

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={(value) => setCollapsed(value)}
        theme="dark"
        breakpoint="lg"
      >
        <div className="flex items-center justify-center p-4">
          <div className="flex items-center gap-2">
            <Avatar src="/vite.svg" size="large" />
            {!collapsed && (
              <span className="text-white font-bold text-lg">NFM-X</span>
            )}
          </div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          items={menuItems}
          selectedKeys={[selectedKey]}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <AntLayout>
        <Header
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px', width: 64, height: 64 }}
          />
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">v1.5.0</span>
            <Avatar icon={<HomeOutlined />} />
          </div>
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
}

export default Layout;