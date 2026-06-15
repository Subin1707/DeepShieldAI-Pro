import { useEffect, useMemo, useState } from "react";

import ChatbotWidget from "./components/chatbot/ChatbotWidget.jsx";
import PageContainer from "./components/layout/PageContainer.jsx";
import AboutPage from "./pages/AboutPage.jsx";
import HistoryPage from "./pages/HistoryPage.jsx";
import HomePage from "./pages/HomePage.jsx";
import ReportPage from "./pages/ReportPage.jsx";
import ResultPage from "./pages/ResultPage.jsx";
import UploadPage from "./pages/UploadPage.jsx";

const pageMeta = {
  "#/": {
    title: "Trang chủ",
    subtitle: "Tổng quan hệ thống phân tích và điều tra deepfake.",
    component: HomePage,
  },
  "#/upload": {
    title: "Tải lên",
    subtitle: "Gửi ảnh hoặc video nghi vấn để phân tích.",
    component: UploadPage,
  },
  "#/results": {
    title: "Kết quả",
    subtitle: "Xem kết luận, mức rủi ro, heatmap và giải thích AI.",
    component: ResultPage,
  },
  "#/history": {
    title: "Lịch sử",
    subtitle: "Xem các lần phân tích đã lưu trong backend.",
    component: HistoryPage,
  },
  "#/reports": {
    title: "Báo cáo",
    subtitle: "Tải xuống báo cáo điều tra đã tạo.",
    component: ReportPage,
  },
  "#/about": {
    title: "Giới thiệu",
    subtitle: "Thông tin về hệ thống và năng lực hiện tại.",
    component: AboutPage,
  },
};

function App() {
  const [hash, setHash] = useState(window.location.hash || "#/");

  useEffect(() => {
    const handleHashChange = () => setHash(window.location.hash || "#/");
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const currentPage = useMemo(() => pageMeta[hash] || pageMeta["#/"], [hash]);
  const Page = currentPage.component;

  return (
    <PageContainer title={currentPage.title} subtitle={currentPage.subtitle}>
      <Page />
      <ChatbotWidget />
    </PageContainer>
  );
}

export default App;
