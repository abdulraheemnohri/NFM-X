import React from "react";
import { Layout as AntLayout, Menu, Typography } from "antd";
import { Link, Outlet } from "react-router-dom";
const { Header, Sider, Content } = AntLayout;
const { Title } = Typography;
export default function Layout() { return <AntLayout><Sider><Title level={4}>NFM-X</Title></Sider><AntLayout><Header>Header</Header><Content><Outlet /></Content></AntLayout></AntLayout>; }