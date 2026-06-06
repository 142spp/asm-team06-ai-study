import React, { useState } from "react";
import styled from "styled-components";
import { mockPreferenceCandidates } from "../mock";
import { Btn, BtnRow, MockNote, MockBadge } from "../styles/common";
import { theme, radius, shadow } from "../styles/theme";

export default function PreferenceModal({ onDone }) {
    const [actions, setActions] = useState({});

    function setAction(field, action) {
        setActions((p) => ({ ...p, [field]: action }));
    }

    return (
        <Overlay>
            <ModalCard>
                <ModalHeader>
                    <span>★ 선호 저장 확인</span>
                    <ModalSub>승인·저장 직후 · 닫으면 결과 요약</ModalSub>
                </ModalHeader>
                <ModalBody>
                    <ModalDesc><MockBadge /> &nbsp;
                        이번 수정에서 <b>반복 가능한 패턴</b>을 선호 후보로 감지했어요.
                        앞으로도 적용할 규칙만 선택하세요.{" "}
                        <Muted>(승인 전엔 장기 저장 안 함)</Muted>
                    </ModalDesc>

                    {mockPreferenceCandidates.map((c) => (
                        <CandCard key={c.field}>
                            <CandRule>{c.rule}</CandRule>
                            <CandBasis>
                                <span>근거</span>
                                <span>{c.basis}</span>
                            </CandBasis>
                            <BtnRow style={{ marginTop: "10px" }}>
                                <Btn $sm $primary={actions[c.field] === "save"}    $ghost={actions[c.field] !== "save"}    onClick={() => setAction(c.field, "save")}>앞으로도 적용</Btn>
                                <Btn $sm $primary={actions[c.field] === "one_time"} $ghost={actions[c.field] !== "one_time"} onClick={() => setAction(c.field, "one_time")}>이번만</Btn>
                                <Btn $sm $warn={actions[c.field] === "dismiss"}   $ghost={actions[c.field] !== "dismiss"}  onClick={() => setAction(c.field, "dismiss")}>무시</Btn>
                            </BtnRow>
                        </CandCard>
                    ))}

                    <ModalFooter>
                        <Muted>'앞으로도 적용'만 User Preference Store에 저장됩니다</Muted>
                        <Btn $primary onClick={onDone}>선택 저장 후 닫기</Btn>
                    </ModalFooter>
                    <MockNote>※ 목데이터 · BE /feedback/analyze 연동 시 실제 후보로 교체</MockNote>
                </ModalBody>
            </ModalCard>
        </Overlay>
    );
}

// ===== styled =====
const Overlay = styled.div`
    position: fixed;
    inset: 0;
    background: rgba(44,43,39,.35);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    padding: 20px;
`;

const ModalCard = styled.div`
    background: ${theme.panel};
    border: 2.5px solid ${theme.line};
    border-radius: ${radius.card};
    box-shadow: 6px 9px 0 rgba(0,0,0,.13);
    width: 100%;
    max-width: 660px;
    max-height: 90vh;
    overflow-y: auto;
`;

const ModalHeader = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    border-bottom: 2px solid ${theme.line};
    font-size: 17px;
    font-weight: 700;
    background: ${theme.panel2};
`;

const ModalSub = styled.span`
    font-size: 12px;
    color: ${theme.ink2};
    font-weight: 400;
`;

const ModalBody = styled.div`
    padding: 18px 20px;
`;

const ModalDesc = styled.p`
    font-size: 13px;
    color: ${theme.ink2};
    margin: 0 0 14px;
`;

const CandCard = styled.div`
    background: #fff;
    border: 2px solid ${theme.line};
    border-radius: 12px 10px 13px 9px;
    padding: 13px 15px;
    margin-bottom: 12px;
    box-shadow: 2px 3px 0 rgba(0,0,0,.07);
`;

const CandRule = styled.div`
    font-size: 15px;
    font-weight: 700;
`;

const CandBasis = styled.div`
    color: ${theme.agent};
    font-size: 12.5px;
    margin-top: 5px;
    display: flex;
    gap: 7px;

    span:first-child { font-weight: 700; }
`;

const ModalFooter = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 16px;
    padding-top: 13px;
    border-top: 2px dashed ${theme.hair};
    flex-wrap: wrap;
    gap: 10px;
`;

const Muted = styled.span`
    font-size: 12px;
    color: ${theme.muted};
`;
