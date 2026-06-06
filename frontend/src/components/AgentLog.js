import React, { useState } from "react";
import styled from "styled-components";
import { mockAgentLog } from "../mock";
import { MockSection } from "../styles/common";
import { theme } from "../styles/theme";

export default function AgentLog() {
    const [open, setOpen] = useState(false);

    return (
        <LogWrap>
            <LogToggle onClick={() => setOpen(!open)}>
                ◧ Agent 실행 로그 {open ? "▲ 접기" : "▼ 펼치기"}
            </LogToggle>
            {open && (
                <LogBody>
                    <MockSection>
                    <LogSteps>
                        {mockAgentLog.map((step, i) => (
                            <React.Fragment key={i}>
                                <LogStep $warn={step.warn}>
                                    {step.label}
                                    {step.sub && <small>({step.sub})</small>}
                                </LogStep>
                                {i < mockAgentLog.length - 1 && <LogArrow>→</LogArrow>}
                            </React.Fragment>
                        ))}
                    </LogSteps>
                    </MockSection>
                    <LogNote>BE 파이프라인이 로그를 반환하면 실제 데이터로 교체</LogNote>
                </LogBody>
            )}
        </LogWrap>
    );
}

// ===== styled =====
const LogWrap = styled.div`
    margin-top: 20px;
`;

const LogToggle = styled.button`
    width: 100%;
    text-align: left;
    font-size: 14px;
    color: ${theme.agent};
    background: #efe9f7;
    border: 2px solid ${theme.agent};
    border-radius: 10px;
    padding: 8px 14px;
    cursor: pointer;
    font-family: inherit;
`;

const LogBody = styled.div`
    margin-top: 8px;
    background: ${theme.panel};
    border: 2px solid ${theme.line};
    border-radius: 10px;
    padding: 14px 18px;
`;

const LogSteps = styled.div`
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
`;

const LogStep = styled.span`
    font-size: 13px;
    border: 1.5px solid ${({ $warn }) => ($warn ? theme.warn : theme.line)};
    background: #fff;
    border-radius: 9px;
    padding: 3px 10px;
    display: flex;
    align-items: center;
    gap: 4px;
    color: ${({ $warn }) => ($warn ? theme.warn : theme.ink)};

    small { color: ${theme.muted}; font-size: 11px; }
`;

const LogArrow = styled.span`
    color: ${theme.muted};
`;

const LogNote = styled.p`
    font-size: 12px;
    color: ${theme.muted};
    margin: 10px 0 0;
`;
