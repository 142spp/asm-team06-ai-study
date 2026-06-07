import React, { useState } from "react";
import styled from "styled-components";
import { mockStore } from "../mock";
import { Card, ScreenHead, StepNum, ScreenTitle, ScreenSub, TypeBadge, Pill, EmptyState, Table, MockNote, MockBadge } from "../styles/common";
import { theme } from "../styles/theme";

const TABS = [
    { key: "tasks",       label: "할 일" },
    { key: "calendar",    label: "일정" },
    { key: "memo",        label: "메모" },
    { key: "risk",        label: "리스크" },
    { key: "pending",     label: "보류" },
    { key: "preferences", label: "선호" },
];

export default function StoreScreen() {
    const [activeTab, setActiveTab] = useState("tasks");

    return (
        <div>
            <ScreenHead>
                <StepNum>5</StepNum>
                <ScreenTitle>로컬 저장소 보기</ScreenTitle>
                <ScreenSub>탭: 할 일 / 일정 / 메모 / 리스크 / 보류 / 선호</ScreenSub>
            </ScreenHead>

            <Card>
                <MockBadge style={{ marginBottom: "10px" }} />
                <SubtabBar>
                    {TABS.map((tab) => {
                        const active = activeTab === tab.key;
                        return (
                            <Subtab key={tab.key} $active={active} onClick={() => setActiveTab(tab.key)}>
                                {tab.label}
                                <TabCount $active={active}>{mockStore[tab.key]?.length ?? 0}</TabCount>
                            </Subtab>
                        );
                    })}
                </SubtabBar>

                {activeTab === "tasks" && (
                    <Table>
                        <thead><tr><th>제목</th><th>담당</th><th>마감</th><th>우선순위</th><th>상태</th></tr></thead>
                        <tbody>
                            {mockStore.tasks.map((t) => (
                                <tr key={t.id}>
                                    <td>{t.title} {t.note && <Pill>{t.note}</Pill>}</td>
                                    <td>{t.assignee}</td>
                                    <td>{t.due}</td>
                                    <td><Pill $danger={t.priority === "high"}>{t.priority === "high" ? "높음" : "보통"}</Pill></td>
                                    <td>{t.status}</td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                )}

                {activeTab === "calendar" && (
                    <div>
                        {mockStore.calendar.map((c) => (
                            <CalRow key={c.id} $seed={c.seed}>
                                <CalWhen>
                                    <b>{c.time ?? "종일"}</b>
                                    {c.allDay && <span>all_day</span>}
                                </CalWhen>
                                <CalInfo>
                                    <b>{c.title}</b>{" "}
                                    {c.note && <Pill>{c.note}</Pill>}
                                    {c.seed && <Pill>기존(seed)</Pill>}
                                    <CalMeta>{c.date} · {c.assignee}</CalMeta>
                                </CalInfo>
                            </CalRow>
                        ))}
                    </div>
                )}

                {activeTab === "memo" && (
                    <EmptyState>
                        메모 저장소가 비어 있어요. ✎<br />
                        <span style={{ fontSize: "14px" }}>'기획서 다시 보기'는 할 일로 수정되어 Task Store로 이동했습니다.</span>
                    </EmptyState>
                )}

                {activeTab === "risk" && (
                    <Table>
                        <thead><tr><th>리스크</th><th>대응(mitigation)</th><th>출처 문장</th></tr></thead>
                        <tbody>
                            {mockStore.risk.map((r) => (
                                <tr key={r.id}>
                                    <td>{r.title}</td>
                                    <td>{r.mitigation}</td>
                                    <SourceCell>"{r.source}"</SourceCell>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                )}

                {activeTab === "pending" && (
                    <Table>
                        <thead><tr><th>항목</th><th>사유</th><th>확인 질문</th></tr></thead>
                        <tbody>
                            {mockStore.pending.map((p) => (
                                <tr key={p.id}>
                                    <td>{p.title}</td>
                                    <td><PendingBadge>모호 일정</PendingBadge></td>
                                    <td>{p.question}</td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                )}

                {activeTab === "preferences" && (
                    <>
                        <Table>
                            <thead><tr><th>저장된 선호 규칙</th><th>적용</th><th>근거</th></tr></thead>
                            <tbody>
                                {mockStore.preferences.map((p) => (
                                    <tr key={p.id}>
                                        <td>{p.rule}</td>
                                        <td><Pill $ok={p.active}>{p.active ? "활성" : "비활성"}</Pill></td>
                                        <td style={{ color: theme.muted }}>{p.basis}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                        <MockNote>※ Guideline Store가 User Preference보다 우선 적용됨</MockNote>
                    </>
                )}

                <MockNote style={{ marginTop: "16px" }}>※ 저장소 목데이터 · GET /storage/{'{kind}'} 연동 시 교체</MockNote>
            </Card>
        </div>
    );
}

// ===== styled =====
const SubtabBar = styled.div`
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
    border-bottom: 2px solid ${theme.line};
    padding-bottom: 10px;
    margin-bottom: 16px;
`;

const Subtab = styled.button`
    font-size: 15px;
    border: 2px solid ${theme.line};
    background: ${({ $active }) => ($active ? theme.ink : "#fff")};
    color: ${({ $active }) => ($active ? "#fff" : theme.ink)};
    border-radius: 11px 8px 12px 7px;
    padding: 5px 13px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 7px;
    font-family: inherit;
`;

const TabCount = styled.span`
    font-size: 12px;
    background: ${({ $active }) => ($active ? "#fff" : theme.panel2)};
    border: 1.5px solid ${theme.hair};
    border-radius: 20px;
    padding: 0 7px;
    color: ${({ $active }) => ($active ? theme.ink : theme.ink2)};
`;

const CalRow = styled.div`
    display: flex;
    gap: 13px;
    align-items: flex-start;
    padding: 11px 12px;
    border: 2px solid ${theme.hair};
    background: #fff;
    border-radius: 11px;
    margin-bottom: 10px;
    opacity: ${({ $seed }) => ($seed ? 0.6 : 1)};
`;

const CalWhen = styled.div`
    font-size: 15px;
    text-align: center;
    flex: none;
    width: 80px;
    border-right: 2px dashed ${theme.hair};
    padding-right: 11px;

    b { display: block; font-size: 18px; color: ${theme.tCal}; }
`;

const CalInfo = styled.div`
    flex: 1;
    font-size: 13px;
`;

const CalMeta = styled.div`
    color: ${theme.muted};
    font-size: 12px;
    margin-top: 3px;
`;

const SourceCell = styled.td`
    font-style: italic;
    color: ${theme.ink2};
`;

const PendingBadge = styled.span`
    display: inline-flex;
    font-size: 13px;
    color: ${theme.warn};
    background: ${theme.warnbg};
    border: 2px solid ${theme.warn};
    border-radius: 8px;
    padding: 1px 9px;
`;
