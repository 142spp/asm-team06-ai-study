import React, { useState } from "react";
import styled from "styled-components";
import GlobalStyle from "./styles/GlobalStyle";
import { Wrap } from "./styles/common";
import { theme, radius, shadow } from "./styles/theme";
import InputScreen from "./components/InputScreen";
import ReviewScreen from "./components/ReviewScreen";
import PreferenceModal from "./components/PreferenceModal";
import SummaryScreen from "./components/SummaryScreen";
import StoreScreen from "./components/StoreScreen";

const STEPS = [
    { id: "input",      label: "입력",      num: 1 },
    { id: "review",     label: "분석·승인", num: 2 },
    { id: "preference", label: "선호 확인", num: 3 },
    { id: "summary",    label: "결과 요약", num: 4 },
    { id: "store",      label: "저장소 보기", num: 5 },
];

// ===== styled =====
const AppTop = styled.header`
    margin-bottom: 8px;
`;

const BrandH1 = styled.h1`
    font-size: 26px;
    font-weight: 700;
    margin: 0;
`;

const BrandP = styled.p`
    margin: 2px 0 0;
    color: ${theme.ink2};
    font-size: 13px;
`;

const FlowNav = styled.nav`
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    padding: 12px 14px;
    background: ${theme.panel};
    border: 2px solid ${theme.line};
    border-radius: 18px 14px 20px 12px;
    box-shadow: ${shadow.card};
    margin-bottom: 24px;
`;

const FlowTab = styled.button`
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 15px;
    border: 2px solid ${theme.line};
    background: ${({ $active }) => ($active ? theme.ink : "#fff")};
    color: ${({ $active }) => ($active ? "#fff" : theme.ink)};
    border-radius: ${radius.btn};
    padding: 6px 13px;
    cursor: pointer;
    font-family: inherit;
    transition: transform 0.08s;

    &:hover { transform: translateY(-1px); }
`;

const FlowNum = styled.span`
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: 2px solid ${({ $active }) => ($active ? "#fff" : theme.line)};
    display: grid;
    place-items: center;
    font-size: 13px;
    background: ${({ $active }) => ($active ? "#fff" : theme.paper)};
    color: ${({ $active }) => ($active ? theme.ink : "inherit")};
`;

const FlowArrow = styled.span`
    color: ${theme.muted};
    font-size: 18px;
`;

const MainContent = styled.main`
    animation: fade 0.2s ease;
    @keyframes fade {
        from { opacity: 0; transform: translateY(4px); }
        to   { opacity: 1; transform: none; }
    }
`;

// ===== App =====
export default function App() {
    const [step, setStep] = useState("input");
    const [analyzeResult, setAnalyzeResult] = useState(null);
    const [rawText, setRawText] = useState("");
    const [approved, setApproved] = useState([]);
    const [excluded, setExcluded] = useState([]);

    function handleAnalyzeDone(result, text) {
        setAnalyzeResult(result);
        setRawText(text);
        setStep("review");
    }

    function handleReviewDone(approvedItems, excludedItems) {
        setApproved(approvedItems);
        setExcluded(excludedItems);
        setStep("preference");
    }

    function handlePreferenceDone() {
        setStep("summary");
    }

    function handleRestart() {
        setStep("input");
        setAnalyzeResult(null);
        setRawText("");
        setApproved([]);
        setExcluded([]);
    }

    return (
        <>
            <GlobalStyle />
            <Wrap>
                <AppTop>
                    <BrandH1>Action Router Agent</BrandH1>
                    <BrandP>비정형 텍스트 → 실행 항목 분해·분류·라우팅 · 로컬 데모</BrandP>
                </AppTop>

                <FlowNav>
                    {STEPS.map((s, i) => {
                        const active = step === s.id;
                        return (
                            <React.Fragment key={s.id}>
                                <FlowTab
                                    $active={active}
                                    onClick={() => {
                                        if (s.id === "input") handleRestart();
                                        if (s.id === "store") setStep("store");
                                    }}
                                >
                                    <FlowNum $active={active}>{s.num}</FlowNum>
                                    {s.label}
                                </FlowTab>
                                {i < STEPS.length - 1 && <FlowArrow>→</FlowArrow>}
                            </React.Fragment>
                        );
                    })}
                </FlowNav>

                <MainContent>
                    {step === "input" && (
                        <InputScreen onAnalyzeDone={handleAnalyzeDone} />
                    )}
                    {step === "review" && analyzeResult && (
                        <ReviewScreen
                            result={analyzeResult}
                            rawText={rawText}
                            onDone={handleReviewDone}
                        />
                    )}
                    {step === "preference" && (
                        <PreferenceModal
                            approved={approved}
                            excluded={excluded}
                            onDone={handlePreferenceDone}
                        />
                    )}
                    {step === "summary" && (
                        <SummaryScreen
                            approved={approved}
                            excluded={excluded}
                            onGoStore={() => setStep("store")}
                            onRestart={handleRestart}
                        />
                    )}
                    {step === "store" && <StoreScreen />}
                </MainContent>
            </Wrap>
        </>
    );
}

