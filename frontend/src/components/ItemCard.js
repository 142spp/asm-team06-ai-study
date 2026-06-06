import React, { useState } from "react";
import styled from "styled-components";
import { mockConflicts } from "../mock";
import { Btn, BtnRow, TypeBadge, Pill, NeedsConfirm, WarnBox, QBox, MockBadge } from "../styles/common";
import { theme, radius } from "../styles/theme";

const TYPE_LABEL = {
    task: "할 일", calendar: "일정", memo: "메모", risk: "리스크", pending: "보류",
};

const WHY_TEXT = {
    task:     "산출물 + 마감일 → 할 일로 분류.",
    calendar: "특정 시각 존재 → 일정으로 분류.",
    memo:     "실행 동사 약함 + 마감 없음 → 메모로 분류.",
    risk:     "조건부 위험 표현 → 리스크. 대응방안은 mitigation에 기록.",
    pending:  "날짜 모호 또는 confidence 낮음 → 보류.",
};

export default function ItemCard({ item, onApprove, onExclude, onEdit }) {
    const [editing, setEditing] = useState(false);
    const [editData, setEditData] = useState({ ...item });
    const conflict = mockConflicts[item.title];

    function handleSaveEdit() {
        onEdit(item, editData);
        setEditing(false);
    }

    return (
        <ItemWrap $flagged={!!conflict}>
            <ItemHeader>
                <TypeBadge type={item.type}>{TYPE_LABEL[item.type] || item.type}</TypeBadge>
                <ItemTitle>{item.title}</ItemTitle>
                {item.priority === "high" && <Pill $danger>우선순위 높음</Pill>}
                {conflict?.type === "duplicate" && <Pill $warn>중복 후보</Pill>}
                {item.needs_confirmation && <NeedsConfirm>확인 필요</NeedsConfirm>}
                <ConfPill>confidence {item.confidence?.toFixed(2) ?? "—"}</ConfPill>
            </ItemHeader>

            <ItemMeta>
                <span>담당 <b>{item.assignee || "—"}</b></span>
                <span>마감 <b>{item.date || (item.date_status === "vague" ? "모호" : "—")}</b></span>
                {item.time && <span>시간 <b>{item.time}</b></span>}
            </ItemMeta>

            <ReasonBox>
                <Source>근거 문장: "{item.source_sentence}"</Source>
                <Why>
                    <WhyIc>↳ 이유</WhyIc>
                    <span>{WHY_TEXT[item.type]}</span>
                </Why>
                {item.recommended_tool && (
                    <ToolRow>추천 Tool: <code>{item.recommended_tool}</code></ToolRow>
                )}
            </ReasonBox>

            {conflict?.type === "time_conflict" && (
                <WarnBox>
                    <b>⚠ 일정 충돌</b> · 기존 일정 「{conflict.with}」과 시간 겹침 <MockBadge />
                    <br />
                    <b>대체 경로 →</b> ① {conflict.suggestion} 제안 &nbsp; ② 수정 &nbsp; ③ Pending 보류
                </WarnBox>
            )}
            {conflict?.type === "duplicate" && (
                <WarnBox>
                    <b>⚠ Task 중복</b> · 기존 「{conflict.with}」과 중복 후보 <MockBadge />
                    <br />
                    <b>대체 경로 →</b> ① 새로 생성 &nbsp; ② 병합 제안 &nbsp; ③ 제외
                </WarnBox>
            )}

            {item.needs_confirmation && item.clarification_question && (
                <QBox>확인 질문: <b>"{item.clarification_question}"</b></QBox>
            )}

            {editing && (
                <EditPanel>
                    <EditPanelHead>
                        <b>✎ 수정 중</b>
                        <span>유형·제목·담당자·마감·시간 편집</span>
                    </EditPanelHead>
                    <EditGrid>
                        <EditField>
                            <span>유형</span>
                            <select value={editData.type} onChange={(e) => setEditData({ ...editData, type: e.target.value })}>
                                <option value="task">할 일</option>
                                <option value="calendar">일정</option>
                                <option value="memo">메모</option>
                                <option value="risk">리스크</option>
                                <option value="pending">보류</option>
                            </select>
                        </EditField>
                        <EditField>
                            <span>제목</span>
                            <input value={editData.title} onChange={(e) => setEditData({ ...editData, title: e.target.value })} />
                        </EditField>
                        <EditField>
                            <span>담당자</span>
                            <input value={editData.assignee || ""} onChange={(e) => setEditData({ ...editData, assignee: e.target.value })} />
                        </EditField>
                        <EditField>
                            <span>마감일</span>
                            <input value={editData.date || ""} onChange={(e) => setEditData({ ...editData, date: e.target.value })} />
                        </EditField>
                        <EditField>
                            <span>시간</span>
                            <input value={editData.time || ""} onChange={(e) => setEditData({ ...editData, time: e.target.value })} />
                        </EditField>
                        <EditField>
                            <span>추천 Tool</span>
                            <input value={editData.recommended_tool || ""} onChange={(e) => setEditData({ ...editData, recommended_tool: e.target.value })} />
                        </EditField>
                    </EditGrid>
                    <BtnRow>
                        <Btn $sm $primary onClick={handleSaveEdit}>저장 후 재검증</Btn>
                        <Btn $sm $ghost onClick={() => setEditing(false)}>취소</Btn>
                        <Btn $sm $warn onClick={() => onExclude(item)}>제외</Btn>
                    </BtnRow>
                </EditPanel>
            )}

            {!editing && (
                <BtnRow style={{ marginTop: "12px" }}>
                    {conflict?.type === "time_conflict" ? (
                        <>
                            <Btn $sm $primary onClick={() => onApprove(item)}>승인(11시로)</Btn>
                            <Btn $sm $ghost onClick={() => setEditing(true)}>수정</Btn>
                            <Btn $sm $warn onClick={() => onExclude(item)}>Pending</Btn>
                        </>
                    ) : conflict?.type === "duplicate" ? (
                        <>
                            <Btn $sm $ghost onClick={() => onApprove(item)}>새로 생성</Btn>
                            <Btn $sm $ghost>병합 제안</Btn>
                            <Btn $sm $warn onClick={() => onExclude(item)}>제외</Btn>
                        </>
                    ) : (
                        <>
                            <Btn $sm $primary onClick={() => onApprove(item)}>승인</Btn>
                            <Btn $sm $ghost onClick={() => setEditing(true)}>수정</Btn>
                            <Btn $sm $ghost onClick={() => onExclude(item)}>제외</Btn>
                        </>
                    )}
                </BtnRow>
            )}
        </ItemWrap>
    );
}

// ===== styled =====
const ItemWrap = styled.div`
    background: #fff;
    border: 2px solid ${({ $flagged }) => ($flagged ? theme.warn : theme.line)};
    border-radius: 13px 10px 14px 9px;
    padding: 14px 15px;
    box-shadow: ${({ $flagged }) =>
        $flagged ? "2px 3px 0 rgba(176,106,16,.18)" : "2px 3px 0 rgba(0,0,0,.07)"};
    margin-bottom: 12px;
`;

const ItemHeader = styled.div`
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
`;

const ItemTitle = styled.span`
    font-size: 15px;
    font-weight: 700;
`;

const ConfPill = styled(Pill)`
    margin-left: auto;
    font-size: 13px;
`;

const ItemMeta = styled.div`
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    margin: 8px 0 0;
    color: ${theme.ink2};
    font-size: 13px;

    b { color: ${theme.ink}; font-weight: 700; }
`;

const ReasonBox = styled.div`
    margin-top: 10px;
    border-top: 2px dashed ${theme.hair};
    padding-top: 9px;
    font-size: 12.5px;
`;

const Source = styled.div`
    color: ${theme.ink2};
    font-style: italic;
`;

const Why = styled.div`
    color: ${theme.agent};
    display: flex;
    gap: 7px;
    margin-top: 4px;
`;

const WhyIc = styled.span`
    font-weight: 700;
    flex: none;
`;

const ToolRow = styled.div`
    margin-top: 5px;
    color: ${theme.ink2};

    code {
        font-family: ui-monospace, 'SF Mono', Menlo, monospace;
        font-size: 12px;
        background: ${theme.panel2};
        border: 1.5px solid ${theme.hair};
        border-radius: 6px;
        padding: 0 6px;
        color: ${theme.agent};
    }
`;

const EditPanel = styled.div`
    margin-top: 11px;
    background: ${theme.panel2};
    border: 2px dashed ${theme.line};
    border-radius: 11px;
    padding: 12px;
`;

const EditPanelHead = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    font-size: 13px;
    color: ${theme.ink2};
`;

const EditGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 10px;

    @media (max-width: 680px) { grid-template-columns: 1fr 1fr; }
`;

const EditField = styled.label`
    display: flex;
    flex-direction: column;
    gap: 3px;

    span { font-size: 12px; color: ${theme.ink2}; }

    input, select {
        border: 2px solid ${theme.hair};
        border-radius: ${radius.sm};
        padding: 5px 9px;
        font-size: 13px;
        font-family: inherit;
        background: #fff;
        color: ${theme.ink};
    }
`;
