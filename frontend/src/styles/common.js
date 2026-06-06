// 공통 styled-components
import styled from "styled-components";
import { theme, radius, shadow } from "./theme";

export const Wrap = styled.div`
    max-width: 960px;
    margin: 0 auto;
    padding: 24px 20px 80px;
`;

// ===== 카드 =====
export const Card = styled.div`
    background: ${theme.panel};
    border: 2.5px solid ${theme.line};
    border-radius: ${radius.card};
    box-shadow: ${shadow.card};
    padding: 22px 24px;
`;

// ===== 버튼 =====
export const Btn = styled.button`
    font-size: ${({ $sm }) => ($sm ? "13px" : "15px")};
    border: 2.5px solid ${({ $warn }) => ($warn ? theme.warn : theme.line)};
    background: ${({ $primary, $warn }) =>
        $primary ? theme.ink : $warn ? theme.warnbg : "#fff"};
    color: ${({ $primary, $warn }) =>
        $primary ? "#fff" : $warn ? theme.warn : theme.ink};
    border-radius: ${radius.btn};
    padding: ${({ $sm }) => ($sm ? "5px 11px" : "8px 16px")};
    cursor: pointer;
    box-shadow: ${shadow.btn};
    white-space: nowrap;
    font-family: inherit;

    &:active { transform: translate(1px, 2px); box-shadow: 1px 1px 0 rgba(0,0,0,.12); }
    &:disabled { opacity: .4; cursor: not-allowed; }
`;

export const BtnRow = styled.div`
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
`;

// ===== 화면 헤더 =====
export const ScreenHead = styled.div`
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 14px;
    flex-wrap: wrap;
`;

export const StepNum = styled.span`
    width: 38px;
    height: 38px;
    background: ${theme.ink};
    color: #fff;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 20px;
    font-weight: 700;
    flex: none;
`;

export const ScreenTitle = styled.h2`
    font-size: 24px;
    margin: 0;
    font-weight: 700;
`;

export const ScreenSub = styled.span`
    color: ${theme.ink2};
    font-size: 13px;
    margin-left: auto;
`;

// ===== 배지 =====
const typeDotColor = {
    task: theme.tTask,
    calendar: theme.tCal,
    memo: theme.tMemo,
    risk: theme.tRisk,
    pending: theme.tPend,
    pend: theme.tPend,
    input: theme.note,
};

export const TypeBadge = styled.span`
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 13.5px;
    border: 2px solid ${({ type }) => type === "input" ? theme.note : theme.line};
    border-style: ${({ type }) => type === "input" ? "dashed" : "solid"};
    background: #fff;
    border-radius: ${radius.badge};
    padding: 2px 9px;
    color: ${({ type }) => type === "input" ? theme.note : theme.ink};

    &::before {
        content: "";
        width: 9px;
        height: 9px;
        border-radius: 50%;
        border: 1.5px solid ${({ type }) => typeDotColor[type] || theme.line};
        background: ${({ type }) => typeDotColor[type] || "transparent"};
    }
`;

export const Pill = styled.span`
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    border: 2px solid ${({ $ok, $warn, $danger }) =>
        $ok ? theme.ok : $warn ? theme.warn : $danger ? theme.danger : theme.hair};
    background: #fff;
    border-radius: 20px;
    padding: 1px 9px;
    color: ${({ $ok, $warn, $danger }) =>
        $ok ? theme.ok : $warn ? theme.warn : $danger ? theme.danger : theme.ink2};
`;

export const NeedsConfirm = styled.span`
    display: inline-flex;
    align-items: center;
    font-size: 13px;
    color: ${theme.warn};
    background: ${theme.warnbg};
    border: 2px solid ${theme.warn};
    border-radius: 8px;
    padding: 1px 9px;
`;

// ===== 공통 박스 =====
export const WarnBox = styled.div`
    margin-top: 10px;
    background: ${theme.warnbg};
    border: 2px solid ${theme.warn};
    border-radius: 10px;
    padding: 9px 11px;
    font-size: 12.8px;
    color: #6a4310;

    b { color: ${theme.warn}; }
`;

export const QBox = styled.div`
    margin-top: 9px;
    background: #eef3fb;
    border: 2px dashed ${theme.note};
    border-radius: 10px;
    padding: 8px 11px;
    font-size: 12.8px;
    color: #214a9e;
`;

export const EmptyState = styled.div`
    font-size: 16px;
    color: ${theme.muted};
    text-align: center;
    padding: 34px 10px;
    border: 2px dashed ${theme.hair};
    border-radius: 12px;
    background: #fff;
`;

export const FieldLabel = styled.div`
    font-size: 16px;
    font-weight: 700;
    margin: 0 0 7px;
    color: ${({ warn }) => (warn ? theme.warn : theme.ink)};
`;

export const MockNote = styled.p`
    font-size: 12px;
    color: ${theme.muted};
    margin: 10px 0 0;
`;

// ===== 테이블 =====
export const Table = styled.table`
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;

    th, td {
        text-align: left;
        padding: 8px 10px;
        border-bottom: 1.5px solid ${theme.hair};
    }
    th {
        font-size: 14px;
        color: ${theme.ink2};
        border-bottom: 2px solid ${theme.line};
    }
    tr:last-child td { border-bottom: none; }
`;

// ===== 목데이터 표시 =====
export const MockBadge = styled.span`
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: ${theme.muted};
    background: ${theme.panel2};
    border: 1.5px dashed ${theme.hair};
    border-radius: 6px;
    padding: 1px 7px;
    vertical-align: middle;

    &::before { content: "📋 목데이터"; }
`;

export const MockSection = styled.div`
    position: relative;
    border: 1.5px dashed ${theme.hair};
    border-radius: 10px;
    padding: 10px 12px;
    margin-top: 8px;

    &::after {
        content: "📋 목데이터";
        position: absolute;
        top: -10px;
        right: 10px;
        font-size: 11px;
        color: ${theme.muted};
        background: ${theme.panel};
        padding: 0 6px;
        border: 1.5px dashed ${theme.hair};
        border-radius: 6px;
    }
`;
