#!/usr/bin/env node
"use strict";

const { BorderStyle } = require("docx");

const DOCX_PAGE_WIDTH = 12240;
const DOCX_PAGE_MARGIN_LEFT = 1224;
const DOCX_PAGE_MARGIN_RIGHT = 1224;
const DOCX_CONTENT_WIDTH = DOCX_PAGE_WIDTH - DOCX_PAGE_MARGIN_LEFT - DOCX_PAGE_MARGIN_RIGHT;

function hp(points) {
    return Math.round(points * 2);
}

function twipFromPt(points) {
    return Math.round(points * 20);
}

function border(color, size = 6, style = BorderStyle.SINGLE) {
    return { color, size, style, space: 0 };
}

function tableBorderless() {
    return {
        top: { color: "FFFFFF", size: 0, style: BorderStyle.NONE },
        bottom: { color: "FFFFFF", size: 0, style: BorderStyle.NONE },
        left: { color: "FFFFFF", size: 0, style: BorderStyle.NONE },
        right: { color: "FFFFFF", size: 0, style: BorderStyle.NONE },
        insideHorizontal: { color: "FFFFFF", size: 0, style: BorderStyle.NONE },
        insideVertical: { color: "FFFFFF", size: 0, style: BorderStyle.NONE },
    };
}

function normalizeWidths(widths, totalWidth) {
    const targetWidth = totalWidth || 0;
    const sourceWidth = widths.reduce((sum, width) => sum + width, 0);
    if (!sourceWidth || !targetWidth) {
        return widths.slice();
    }

    const scaled = widths.map((width) => Math.max(1, Math.round((width / sourceWidth) * targetWidth)));
    const delta = targetWidth - scaled.reduce((sum, width) => sum + width, 0);
    if (delta !== 0 && scaled.length > 0) {
        scaled[scaled.length - 1] += delta;
    }
    return scaled;
}

module.exports = {
    DOCX_CONTENT_WIDTH,
    DOCX_PAGE_MARGIN_LEFT,
    DOCX_PAGE_MARGIN_RIGHT,
    DOCX_PAGE_WIDTH,
    hp,
    normalizeWidths,
    twipFromPt,
    border,
    tableBorderless,
};
