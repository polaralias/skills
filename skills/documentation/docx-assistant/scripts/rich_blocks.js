#!/usr/bin/env node
"use strict";

const {
    AlignmentType,
    BorderStyle,
    Paragraph,
    ShadingType,
    Table,
    TableCell,
    TableLayoutType,
    TableRow,
    TextRun,
    VerticalAlign,
    WidthType,
} = require("docx");
const { DOCX_CONTENT_WIDTH, hp, twipFromPt, border, tableBorderless } = require("./docx_layout_utils");

const COLORS = {
    orange: "FF4500",
    blue: "3424FF",
    black: "222222",
    darkGrey: "555555",
    mediumGrey: "B8B2B0",
    lightGrey: "F2F0ED",
    faintGrey: "FAF7F5",
    yellow: "FFBF4D",
    turquoise: "45D1D4",
    orangeTint: "FF9980",
    softOrange: "FFF0EA",
    softBlue: "EAEDFF",
    softYellow: "FFF4D8",
    softMint: "EAF8F4",
    deepTeal: "1E7D7F",
    skyBlue: "87ABFF",
    purpleTint: "9C94FA",
    pink: "FF91CC",
    softSky: "F3F7FF",
    softLavender: "F5F1FF",
};

const CUE_VARIANTS = {
    visual: {
        label: "VISUAL",
        icon: null,
        fill: COLORS.softBlue,
        border: COLORS.blue,
        labelColor: COLORS.blue,
        iconColor: COLORS.blue,
        titleColor: COLORS.blue,
        bodyColor: COLORS.darkGrey,
        bodyItalics: true,
    },
    keyInfo: {
        label: "KEY INFO",
        icon: null,
        fill: COLORS.softSky,
        border: COLORS.skyBlue,
        labelColor: "426DDC",
        iconColor: "426DDC",
        titleColor: "426DDC",
        bodyColor: COLORS.darkGrey,
        bodyItalics: false,
    },
    takeaway: {
        label: "TAKEAWAY",
        icon: null,
        fill: COLORS.softLavender,
        border: COLORS.purpleTint,
        labelColor: "6F63DA",
        iconColor: "6F63DA",
        titleColor: "6F63DA",
        bodyColor: COLORS.darkGrey,
        bodyItalics: false,
    },
    warning: {
        label: "WARNING",
        icon: null,
        fill: COLORS.softOrange,
        border: COLORS.orangeTint,
        labelColor: "D95A00",
        iconColor: "D95A00",
        titleColor: COLORS.orange,
        bodyColor: COLORS.darkGrey,
        bodyItalics: false,
    },
    tip: {
        label: "TIP",
        icon: null,
        fill: COLORS.softMint,
        border: COLORS.turquoise,
        labelColor: COLORS.deepTeal,
        iconColor: COLORS.deepTeal,
        titleColor: COLORS.deepTeal,
        bodyColor: COLORS.darkGrey,
        bodyItalics: false,
    },
};

function cueTextRun(text, options = {}) {
    return new TextRun({
        text,
        font: options.font,
        size: hp(options.size || 10),
        color: options.color || COLORS.black,
        bold: options.bold || false,
        italics: options.italics || false,
        allCaps: options.allCaps || false,
        characterSpacing: options.characterSpacing,
        break: options.breakCount,
    });
}

function paragraph(children, options = {}) {
    return new Paragraph({
        children,
        alignment: options.alignment || AlignmentType.LEFT,
        spacing: options.spacing,
        keepNext: options.keepNext,
        indent: options.indent,
        border: options.border,
    });
}

function resolveCueVariant(variantName) {
    const variant = CUE_VARIANTS[variantName];
    if (!variant) {
        throw new Error(`Unknown cue variant: ${variantName}`);
    }
    return variant;
}

function normalizeBody(body) {
    if (typeof body === "string") {
        const commaCount = (body.match(/,\s+/g) || []).length;
        if (commaCount >= 3 && !body.includes("\n")) {
            throw new Error("Callout body looks like a comma-joined list. Use body blocks with { type: \"bullets\", items: [...] } instead.");
        }
    }
    if (Array.isArray(body)) {
        return body;
    }
    return [body];
}

function isBodyBlock(value) {
    return value && typeof value === "object" && !Array.isArray(value) && typeof value.type === "string";
}

function makeCueBlock(fontName, variantName, body, options = {}) {
    const variant = resolveCueVariant(variantName);
    const label = (options.label || variant.label).toUpperCase();
    const icon = options.icon === undefined ? variant.icon : options.icon;
    const bodyLines = normalizeBody(body);
    const bodyItalics = options.bodyItalics === undefined ? variant.bodyItalics : options.bodyItalics;
    const titleColor = options.titleColor || variant.titleColor || variant.labelColor;
    const bodyColor = options.bodyColor || variant.bodyColor;

    const children = [
        paragraph(
            [
                ...(icon
                    ? [
                        cueTextRun(`${icon} `, {
                            font: fontName,
                            size: 8.8,
                            color: options.iconColor || variant.iconColor,
                            bold: true,
                        }),
                    ]
                    : []),
                cueTextRun(label, {
                    font: fontName,
                    size: 8.9,
                    color: options.labelColor || variant.labelColor,
                    bold: true,
                    allCaps: true,
                    characterSpacing: 28,
                }),
            ],
            {
                spacing: { before: 0, after: twipFromPt(options.title ? 1.5 : 2), line: twipFromPt(11.5) },
                keepNext: true,
            },
        ),
    ];

    if (options.title) {
        children.push(
            paragraph(
                [
                    cueTextRun(options.title, {
                        font: fontName,
                        size: 10,
                        color: titleColor,
                        bold: true,
                    }),
                ],
                {
                    spacing: { before: 0, after: twipFromPt(2), line: twipFromPt(12.5) },
                    keepNext: true,
                },
            ),
        );
    }

    for (let index = 0; index < bodyLines.length; index += 1) {
        const line = bodyLines[index];
        if (isBodyBlock(line)) {
            if (line.type === "paragraph") {
                children.push(
                    paragraph(
                        [
                            cueTextRun(line.text, {
                                font: fontName,
                                size: 9.9,
                                color: bodyColor,
                                italics: bodyItalics,
                            }),
                        ],
                        {
                            spacing: {
                                before: 0,
                                after: index === bodyLines.length - 1 ? 0 : twipFromPt(2.25),
                                line: twipFromPt(13.2),
                            },
                        },
                    ),
                );
                continue;
            }
            if (line.type === "bullets") {
                for (let bulletIndex = 0; bulletIndex < line.items.length; bulletIndex += 1) {
                    children.push(
                        new Paragraph({
                            numbering: { reference: "docx-bullets", level: 0 },
                            spacing: {
                                before: 0,
                                after: bulletIndex === line.items.length - 1 ? 0 : twipFromPt(2),
                                line: twipFromPt(13.2),
                            },
                            children: [
                                cueTextRun(line.items[bulletIndex], {
                                    font: fontName,
                                    size: 9.9,
                                    color: bodyColor,
                                    italics: false,
                                }),
                            ],
                        }),
                    );
                }
                continue;
            }
            throw new Error(`Unsupported callout body block type: ${line.type}`);
        }
        if (typeof line !== "string") {
            throw new TypeError(`Callout body line must be a string or supported body block, received ${Array.isArray(line) ? "array" : typeof line}`);
        }
        children.push(
            paragraph(
                [
                    cueTextRun(line, {
                        font: fontName,
                        size: 9.9,
                        color: bodyColor,
                        italics: bodyItalics,
                    }),
                ],
                {
                    spacing: {
                        before: 0,
                        after: index === bodyLines.length - 1 ? 0 : twipFromPt(2.25),
                        line: twipFromPt(13.2),
                    },
                },
            ),
        );
    }

    return new Table({
        alignment: AlignmentType.LEFT,
        width: { size: options.width || DOCX_CONTENT_WIDTH, type: WidthType.DXA },
        columnWidths: [options.width || DOCX_CONTENT_WIDTH],
        layout: TableLayoutType.FIXED,
        borders: tableBorderless(),
        rows: [
            new TableRow({
                cantSplit: true,
                children: [
                    new TableCell({
                        width: { size: options.width || DOCX_CONTENT_WIDTH, type: WidthType.DXA },
                        shading: { fill: options.fill || variant.fill, type: ShadingType.CLEAR, color: "auto" },
                        verticalAlign: VerticalAlign.CENTER,
                        margins: { top: 95, bottom: 95, left: 130, right: 145 },
                        borders: {
                            top: border(options.borderColor || variant.border, 10),
                            bottom: border(options.borderColor || variant.border, 6),
                            left: border(options.fill || variant.fill, 0, BorderStyle.NONE),
                            right: border(options.fill || variant.fill, 0, BorderStyle.NONE),
                        },
                        children,
                    }),
                ],
            }),
        ],
    });
}

function makeVisualCue(fontName, body, options = {}) {
    return makeCueBlock(fontName, "visual", body, options);
}

function makeKeyInfoCue(fontName, body, options = {}) {
    return makeCueBlock(fontName, "keyInfo", body, options);
}

function makeTakeawayCue(fontName, body, options = {}) {
    return makeCueBlock(fontName, "takeaway", body, options);
}

function makeWarningCue(fontName, body, options = {}) {
    return makeCueBlock(fontName, "warning", body, options);
}

function makeTipCue(fontName, body, options = {}) {
    return makeCueBlock(fontName, "tip", body, options);
}

module.exports = {
    COLORS,
    CUE_VARIANTS,
    makeCueBlock,
    makeVisualCue,
    makeKeyInfoCue,
    makeTakeawayCue,
    makeWarningCue,
    makeTipCue,
};
