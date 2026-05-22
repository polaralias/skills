#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const {
    AlignmentType,
    BorderStyle,
    Document,
    Footer,
    Header,
    HeadingLevel,
    ImageRun,
    LevelFormat,
    PageBreak,
    PageNumber,
    Paragraph,
    SectionType,
    ShadingType,
    Table,
    TableCell,
    TableLayoutType,
    TableRow,
    TextRun,
    VerticalAlign,
    WidthType,
} = require("docx");
const { COLORS, makeCueBlock } = require("./rich_blocks");
const { DOCX_CONTENT_WIDTH, hp, normalizeWidths, twipFromPt, border, tableBorderless } = require("./docx_layout_utils");

const ROOT = path.resolve(__dirname, "..");
const LOGO = process.env.DOCX_THEME_LOGO_PATH || path.join(ROOT, "assets", "logo.png");
const LOGO_PROTECTED = process.env.DOCX_THEME_LOGO_PROTECTED_PATH || process.env.DOCX_THEME_LOGO_PATH || path.join(ROOT, "assets", "logo-protected.png");
const ACCENT_ICON = process.env.DOCX_THEME_ACCENT_ICON_PATH || path.join(ROOT, "assets", "icon.png");
const COVER_FONT = process.env.DOCX_THEME_DISPLAY_FONT_NAME || "Aptos Serif";
const BRAND_NAME = process.env.DOCX_THEME_BRAND_NAME || "Brand";
const LOGO_PLATE_FILL = COLORS.faintGrey;
const LOGO_PLATE_BORDER = COLORS.mediumGrey;
const LOGO_PROTECTED_WIDTH = 1412;
const LOGO_PROTECTED_HEIGHT = 484;
const TITLE_PARAGRAPH_BORDER = {
    bottom: {
        style: BorderStyle.SINGLE,
        size: 12,
        color: COLORS.orange,
        space: 0,
    },
};
const INVISIBLE_HEADING_BORDER = {
    bottom: {
        style: BorderStyle.SINGLE,
        size: 2,
        color: "FFFFFF",
        space: 0,
    },
};

const PAGE = {
    width: 12240,
    height: 15840,
    marginTop: 1224,
    marginRight: 1224,
    marginBottom: 1008,
    marginLeft: 1224,
    header: 504,
    footer: 504,
    gutter: 0,
};
const CONTENT_WIDTH = DOCX_CONTENT_WIDTH;

const PANEL_VARIANTS = {
    neutral: { fill: COLORS.faintGrey, border: COLORS.orangeTint, title: COLORS.black },
    action: { fill: COLORS.softYellow, border: COLORS.yellow, title: COLORS.orange },
    example: { fill: COLORS.softMint, border: COLORS.turquoise, title: COLORS.deepTeal },
};

function fileExists(target) {
    try {
        fs.accessSync(target, fs.constants.F_OK);
        return true;
    } catch {
        return false;
    }
}

function readImage(filePath) {
    return fs.readFileSync(filePath);
}

function choosePrimaryFont() {
    const roots = [
        path.join(process.env.WINDIR || "C:\\Windows", "Fonts"),
        path.join(process.env.LOCALAPPDATA || "", "Microsoft", "Windows", "Fonts"),
        "/Library/Fonts",
        "/System/Library/Fonts",
        path.join(process.env.HOME || "", ".fonts"),
        path.join(process.env.HOME || "", ".local", "share", "fonts"),
    ].filter(Boolean);

    for (const root of roots) {
        if (!fileExists(root)) {
            continue;
        }
        let names;
        try {
            names = fs.readdirSync(root, { withFileTypes: true })
                .filter((entry) => entry.isFile())
                .map((entry) => entry.name.toLowerCase());
        } catch {
            continue;
        }
        if (names.some((name) => name.includes("helvetica"))) {
            return "Helvetica";
        }
    }

    return "Arial";
}

function formatTodayLabel(date = new Date()) {
    return date.toLocaleDateString("en-GB", {
        day: "numeric",
        month: "long",
        year: "numeric",
    });
}

function run(text, options = {}) {
    if (typeof text !== "string") {
        throw new TypeError(`TextRun content must be a string, received ${Array.isArray(text) ? "array" : typeof text}`);
    }
    return new TextRun({
        text,
        font: options.font,
        size: hp(options.size || 10.5),
        color: options.color || COLORS.black,
        bold: options.bold || false,
        italics: options.italics || false,
    });
}

function para(children, options = {}) {
    return new Paragraph({
        children,
        heading: options.heading,
        spacing: options.spacing,
        alignment: options.alignment || AlignmentType.LEFT,
        keepNext: options.keepNext,
        border: options.border,
        style: options.style,
    });
}

function spacer(heightPt = 6) {
    return para(
        [run(" ", { font: "Arial", size: 1, color: "FFFFFF" })],
        { spacing: { after: twipFromPt(heightPt), line: 240 } },
    );
}

function makePageBreak() {
    return new Paragraph({ children: [new PageBreak()] });
}

function fitContentWidths(widths) {
    return normalizeWidths(widths, CONTENT_WIDTH);
}

function makeLogoPlate(imageWidth, imageHeight, options = {}) {
    const altDescription = options.altDescription || `${BRAND_NAME} logo`;
    const width = imageWidth;
    const height = imageHeight || Math.round((imageWidth * LOGO_PROTECTED_HEIGHT) / LOGO_PROTECTED_WIDTH);

    if (!fileExists(LOGO_PROTECTED)) {
        return new Paragraph({
            alignment: options.alignment || AlignmentType.LEFT,
            spacing: { before: 0, after: 0 },
            children: [run(BRAND_NAME, { font: COVER_FONT, size: 12, color: COLORS.black })],
        });
    }

    return new Paragraph({
        alignment: options.alignment || AlignmentType.LEFT,
        spacing: { before: 0, after: 0 },
        children: [
            new ImageRun({
                type: "png",
                data: readImage(LOGO_PROTECTED),
                transformation: { width, height },
                altText: {
                    title: "Protected logo",
                    description: altDescription,
                    name: "Protected logo",
                },
            }),
        ],
    });
}

function makeBodyParagraph(fontName, text, options = {}) {
    if (typeof text !== "string") {
        throw new TypeError(`Body paragraph text must be a string, received ${Array.isArray(text) ? "array" : typeof text}`);
    }
    return para(
        [
            run(text, {
                font: options.font || fontName,
                size: options.size || 10.5,
                color: options.color || COLORS.black,
                bold: options.bold || false,
                italics: options.italics || false,
            }),
        ],
        {
            spacing: options.spacing || {
                before: 0,
                after: twipFromPt(6),
                line: twipFromPt(13.5),
            },
            keepNext: options.keepNext,
            style: options.style,
        },
    );
}

function makePageContextLabel(fontName, text) {
    return para(
        [run(text, { font: COVER_FONT, size: 14, color: COLORS.blue })],
        {
            style: "DocxKicker",
            keepNext: true,
        },
    );
}

function makeDisplayKicker(text) {
    return para(
        [run(text, { font: COVER_FONT, size: 14, color: COLORS.blue })],
        {
            style: "DocxKicker",
            keepNext: true,
        },
    );
}

function makeMajorHeading(text) {
    return para(
        [run(text, { font: COVER_FONT, size: 19, color: COLORS.black })],
        {
            style: "Heading1",
            heading: HeadingLevel.HEADING_1,
            keepNext: true,
            spacing: { before: 0, after: twipFromPt(4) },
            border: INVISIBLE_HEADING_BORDER,
        },
    );
}

function makeSubheading(fontName, text) {
    return para(
        [run(text, { font: fontName, size: 15, color: COLORS.black, bold: fontName !== COVER_FONT })],
        {
            style: "Heading2",
            heading: HeadingLevel.HEADING_2,
            keepNext: true,
            spacing: { before: twipFromPt(4), after: twipFromPt(5) },
            border: INVISIBLE_HEADING_BORDER,
        },
    );
}

function makeBulletedList(fontName, items, options = {}) {
    return items.map((item, index) =>
        new Paragraph({
            numbering: { reference: "docx-bullets", level: 0 },
            spacing: {
                before: 0,
                after: twipFromPt(index === items.length - 1 ? (options.lastSpacingAfter || options.spacingAfter || 2.5) : (options.spacingAfter || 2.5)),
                line: twipFromPt(options.lineHeight || 13.5),
            },
            children: [
                run(item, {
                    font: fontName,
                    size: options.fontSize || 10.3,
                    color: options.color || COLORS.black,
                }),
            ],
        }),
    );
}

function makeSummaryTable(fontName, rows) {
    const widths = fitContentWidths([2200, 6800]);
    return new Table({
        alignment: AlignmentType.LEFT,
        width: { size: CONTENT_WIDTH, type: WidthType.DXA },
        columnWidths: widths,
        layout: TableLayoutType.FIXED,
        borders: {
            top: border(COLORS.black, 10),
            bottom: border(COLORS.black, 10),
            left: border(COLORS.lightGrey, 6),
            right: border(COLORS.lightGrey, 6),
            insideHorizontal: border(COLORS.lightGrey, 6),
            insideVertical: border(COLORS.lightGrey, 6),
        },
        rows: rows.map(([label, value], index) =>
            new TableRow({
                cantSplit: true,
                children: [
                    new TableCell({
                        width: { size: widths[0], type: WidthType.DXA },
                        shading: { fill: index % 2 === 0 ? COLORS.faintGrey : COLORS.lightGrey, type: ShadingType.CLEAR, color: "auto" },
                        margins: { top: 100, bottom: 100, left: 120, right: 120 },
                        verticalAlign: VerticalAlign.CENTER,
                        children: [makeBodyParagraph(fontName, label, { size: 9.5, color: COLORS.darkGrey, bold: true, spacing: { before: 0, after: 0, line: twipFromPt(12.5) } })],
                    }),
                    new TableCell({
                        width: { size: widths[1], type: WidthType.DXA },
                        margins: { top: 100, bottom: 100, left: 120, right: 120 },
                        verticalAlign: VerticalAlign.CENTER,
                        children: [makeBodyParagraph(fontName, value, { size: 10, spacing: { before: 0, after: 0, line: twipFromPt(13.5) } })],
                    }),
                ],
            }),
        ),
    });
}

function makeMetaBar(fontName, leftLabel, leftValue, rightLabel, rightValue) {
    for (const [name, value] of Object.entries({ leftLabel, leftValue, rightLabel, rightValue })) {
        if (typeof value !== "string") {
            throw new TypeError(`Meta bar ${name} must be a single-line string. Move lists into a callout body.`);
        }
    }
    const widths = fitContentWidths([7440, 1920]);
    return new Table({
        alignment: AlignmentType.LEFT,
        width: { size: CONTENT_WIDTH, type: WidthType.DXA },
        columnWidths: widths,
        layout: TableLayoutType.FIXED,
        borders: tableBorderless(),
        rows: [
            new TableRow({
                cantSplit: true,
                children: [
                    new TableCell({
                        width: { size: widths[0], type: WidthType.DXA },
                        shading: { fill: COLORS.softBlue, type: ShadingType.CLEAR, color: "auto" },
                        verticalAlign: VerticalAlign.CENTER,
                        margins: { top: 95, bottom: 95, left: 120, right: 120 },
                        borders: {
                            left: border(COLORS.blue, 24),
                            top: border(COLORS.softBlue, 0, BorderStyle.NONE),
                            bottom: border(COLORS.softBlue, 0, BorderStyle.NONE),
                            right: border(COLORS.softBlue, 0, BorderStyle.NONE),
                        },
                        children: [
                            new Paragraph({
                                spacing: { before: 0, after: 0, line: twipFromPt(12.5) },
                                children: [
                                    run(`${leftLabel} `, { font: fontName, size: 9.5, color: COLORS.darkGrey, bold: true }),
                                    run(leftValue, { font: fontName, size: 9.5, color: COLORS.darkGrey }),
                                ],
                            }),
                        ],
                    }),
                    new TableCell({
                        width: { size: widths[1], type: WidthType.DXA },
                        shading: { fill: COLORS.softBlue, type: ShadingType.CLEAR, color: "auto" },
                        verticalAlign: VerticalAlign.CENTER,
                        margins: { top: 95, bottom: 95, left: 120, right: 120 },
                        borders: {
                            left: border(COLORS.softBlue, 0, BorderStyle.NONE),
                            top: border(COLORS.softBlue, 0, BorderStyle.NONE),
                            bottom: border(COLORS.softBlue, 0, BorderStyle.NONE),
                            right: border(COLORS.softBlue, 0, BorderStyle.NONE),
                        },
                        children: [
                            new Paragraph({
                                alignment: AlignmentType.RIGHT,
                                spacing: { before: 0, after: 0, line: twipFromPt(12.5) },
                                children: [
                                    run(`${rightLabel} `, { font: fontName, size: 9.5, color: COLORS.darkGrey, bold: true }),
                                    run(rightValue, { font: fontName, size: 9.5, color: COLORS.darkGrey }),
                                ],
                            }),
                        ],
                    }),
                ],
            }),
        ],
    });
}

function makeSectionOpening(fontName, options = {}) {
    const blocks = [];

    if (options.kicker) {
        blocks.push(makePageContextLabel(fontName, options.kicker));
    }

    blocks.push(makeMajorHeading(options.heading || "Section heading"));

    if (options.meta) {
        blocks.push(
            makeMetaBar(
                fontName,
                options.meta.leftLabel,
                options.meta.leftValue,
                options.meta.rightLabel,
                options.meta.rightValue,
            ),
        );
        if (options.metaSpacerPt !== 0) {
            blocks.push(spacer(options.metaSpacerPt || 4));
        }
    }

    const introLines = Array.isArray(options.intro)
        ? options.intro.filter(Boolean)
        : (options.intro ? [options.intro] : []);
    introLines.forEach((line, index) => {
        const isLast = index === introLines.length - 1;
        blocks.push(
            makeBodyParagraph(fontName, line, {
                size: options.introSize || 10.8,
                color: options.introColor || COLORS.black,
                spacing: {
                    before: 0,
                    after: twipFromPt(isLast ? (options.introAfterPt || 7) : (options.introBetweenPt || 4)),
                    line: twipFromPt(options.introLineHeight || 15),
                },
            }),
        );
    });

    if (options.afterIntroSpacerPt) {
        blocks.push(spacer(options.afterIntroSpacerPt));
    }

    return blocks;
}

function makeDataTable(fontName, headers, rows, widths, options = {}) {
    const tableWidths = options.fillWidth === false ? widths : fitContentWidths(widths);
    const tableWidth = options.fillWidth === false
        ? tableWidths.reduce((acc, value) => acc + value, 0)
        : CONTENT_WIDTH;
    return new Table({
        alignment: AlignmentType.LEFT,
        width: { size: tableWidth, type: WidthType.DXA },
        columnWidths: tableWidths,
        layout: TableLayoutType.FIXED,
        borders: {
            top: border(COLORS.black, 10),
            bottom: border(COLORS.black, 10),
            left: border(COLORS.lightGrey, 6),
            right: border(COLORS.lightGrey, 6),
            insideHorizontal: border(COLORS.lightGrey, 6),
            insideVertical: border(COLORS.lightGrey, 6),
        },
        rows: [
            new TableRow({
                tableHeader: true,
                cantSplit: true,
                children: headers.map((header, index) =>
                    new TableCell({
                        width: { size: tableWidths[index], type: WidthType.DXA },
                        shading: { fill: COLORS.black, type: ShadingType.CLEAR, color: "auto" },
                        margins: { top: 100, bottom: 100, left: 120, right: 120 },
                        verticalAlign: VerticalAlign.CENTER,
                        children: [makeBodyParagraph(fontName, header, { size: 9.5, color: "FFFFFF", bold: true, spacing: { before: 0, after: 0, line: twipFromPt(12.5) } })],
                    }),
                ),
            }),
            ...rows.map((row, rowIndex) =>
                new TableRow({
                    cantSplit: true,
                    children: row.map((value, index) =>
                        new TableCell({
                            width: { size: tableWidths[index], type: WidthType.DXA },
                            shading: { fill: rowIndex % 2 === 0 ? "FFFFFF" : COLORS.faintGrey, type: ShadingType.CLEAR, color: "auto" },
                            margins: { top: 95, bottom: 95, left: 120, right: 120 },
                            verticalAlign: VerticalAlign.CENTER,
                            children: [makeBodyParagraph(fontName, value, { size: 10, spacing: { before: 0, after: 0, line: twipFromPt(13.5) } })],
                        }),
                    ),
                }),
            ),
        ],
    });
}

function makeCard(fontName, title, items, variantName = "neutral") {
    const variant = PANEL_VARIANTS[variantName] || PANEL_VARIANTS.neutral;
    return new Table({
        alignment: AlignmentType.LEFT,
        width: { size: CONTENT_WIDTH, type: WidthType.DXA },
        columnWidths: [CONTENT_WIDTH],
        layout: TableLayoutType.FIXED,
        borders: tableBorderless(),
        rows: [
            new TableRow({
                cantSplit: true,
                children: [
                    new TableCell({
                        width: { size: CONTENT_WIDTH, type: WidthType.DXA },
                        shading: { fill: variant.fill, type: ShadingType.CLEAR, color: "auto" },
                        margins: { top: 120, bottom: 120, left: 140, right: 160 },
                        borders: {
                            top: border(variant.border, 10),
                            bottom: border(variant.border, 6),
                            left: border(variant.fill, 0, BorderStyle.NONE),
                            right: border(variant.fill, 0, BorderStyle.NONE),
                        },
                        children: [
                            makeBodyParagraph(fontName, title, { size: 10.6, color: variant.title, bold: true, keepNext: true, spacing: { before: 0, after: twipFromPt(3), line: twipFromPt(13) } }),
                            ...makeBulletedList(fontName, items, { fontSize: 10.1, spacingAfter: 2.5 }),
                        ],
                    }),
                ],
            }),
        ],
    });
}

function makeBrandedHeader() {
    return new Header({
        children: [
            makeLogoPlate(150, undefined, {
                altDescription: `${BRAND_NAME} logo in header`,
            }),
        ],
    });
}

function makePageNumberFooter(fontName) {
    return new Footer({
        children: [
            new Paragraph({
                alignment: AlignmentType.RIGHT,
                spacing: { before: 0, after: 0 },
                children: [
                    run("Page ", { font: fontName, size: 9.5, color: COLORS.darkGrey }),
                    new TextRun({
                        children: [PageNumber.CURRENT],
                        font: fontName,
                        size: hp(9.5),
                        color: COLORS.darkGrey,
                    }),
                ],
            }),
        ],
    });
}

function makeBrandedCover(options = {}) {
    const introBody = options.introBody === undefined ? [
        "This example shows the default themed visual system for a fresh branded document.",
        "Use the shared layout primitives and cue blocks so new outputs inherit the same page rhythm by default.",
    ] : options.introBody;
    const coverWidths = fitContentWidths([7600, 1760]);
    const cue = options.cue === undefined ? {
        label: "LAYOUT",
        title: "Why this layout works",
        body: [
            "The first page pairs a strong title hierarchy with calm accents and neutral surfaces so the document feels branded without becoming noisy.",
            "The summary table and labelled cue create scanability before the document moves into denser working pages.",
        ],
    } : options.cue;

    const introChildren = introBody.map((text, index) => makeBodyParagraph(options.bodyFontName, text, {
        size: index === 0 ? 11 : 10.3,
        color: index === 0 ? COLORS.black : COLORS.darkGrey,
        spacing: {
            before: 0,
            after: index === introBody.length - 1 ? 0 : twipFromPt(5),
            line: twipFromPt(index === 0 ? 15 : 14),
        },
    }));

    const coverChildren = [
        makeLogoPlate(228, undefined, {
            altDescription: `${BRAND_NAME} logo`,
        }),
        spacer(8),
        makeDisplayKicker(options.eyebrow || "Example document"),
        para(
            [run(options.title || "Branded example document", { font: COVER_FONT, size: 28, color: COLORS.black })],
            { style: "Title", spacing: { before: 0, after: twipFromPt(6) }, border: TITLE_PARAGRAPH_BORDER },
        ),
        makeBodyParagraph(options.bodyFontName, options.subtitle || "", {
            size: 11.5,
            color: COLORS.darkGrey,
            italics: true,
            style: "DocxSubtitle",
            spacing: { before: 0, after: twipFromPt(14), line: twipFromPt(15) },
        }),
    ];

    if (introChildren.length > 0) {
        coverChildren.push(new Table({
            alignment: AlignmentType.LEFT,
            width: { size: CONTENT_WIDTH, type: WidthType.DXA },
            columnWidths: coverWidths,
            layout: TableLayoutType.FIXED,
            borders: tableBorderless(),
            rows: [
                new TableRow({
                    cantSplit: true,
                    children: [
                        new TableCell({
                            width: { size: coverWidths[0], type: WidthType.DXA },
                            shading: { fill: COLORS.faintGrey, type: ShadingType.CLEAR, color: "auto" },
                            margins: { top: 150, bottom: 150, left: 160, right: 160 },
                            borders: {
                                top: border(COLORS.black, 10),
                                bottom: border(COLORS.black, 10),
                                left: border(COLORS.faintGrey, 0, BorderStyle.NONE),
                                right: border(COLORS.faintGrey, 0, BorderStyle.NONE),
                            },
                            children: introChildren,
                        }),
                        new TableCell({
                            width: { size: coverWidths[1], type: WidthType.DXA },
                            shading: { fill: COLORS.softBlue, type: ShadingType.CLEAR, color: "auto" },
                            verticalAlign: VerticalAlign.CENTER,
                            margins: { top: 110, bottom: 110, left: 110, right: 110 },
                            borders: {
                                top: border(COLORS.blue, 10),
                                bottom: border(COLORS.blue, 10),
                                left: border(COLORS.softBlue, 0, BorderStyle.NONE),
                                right: border(COLORS.softBlue, 0, BorderStyle.NONE),
                            },
                            children: [
                                para(
                                    [
                                        ...(fileExists(ACCENT_ICON)
                                            ? [new ImageRun({
                                                type: "png",
                                                data: readImage(ACCENT_ICON),
                                                transformation: { width: 72, height: 72 },
                                            })]
                                            : [run(BRAND_NAME.slice(0, 1).toUpperCase(), { font: COVER_FONT, size: 20, color: COLORS.blue })]),
                                    ],
                                    { alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0 } },
                                ),
                            ],
                        }),
                    ],
                }),
            ],
        }));
    }

    if (cue) {
        coverChildren.push(
            spacer(9),
            makeCueBlock(options.bodyFontName, "visual", cue.body, {
            label: cue.label,
            title: cue.title,
            bodyItalics: false,
            }),
        );
    }

    if (options.summaryRows && options.summaryRows.length > 0) {
        coverChildren.push(spacer(5), makeSummaryTable(options.bodyFontName, options.summaryRows));
    }

    return coverChildren;
}

function makeBrandedDocument(options = {}) {
    const fontName = options.bodyFontName || choosePrimaryFont();
    const pageProperties = {
        page: {
            size: { width: PAGE.width, height: PAGE.height },
            margin: {
                top: PAGE.marginTop,
                right: PAGE.marginRight,
                bottom: PAGE.marginBottom,
                left: PAGE.marginLeft,
                header: PAGE.header,
                footer: PAGE.footer,
                gutter: PAGE.gutter,
            },
        },
    };

    return new Document({
        creator: BRAND_NAME,
        lastModifiedBy: BRAND_NAME,
        title: options.title || "Branded document",
        description: options.description || "A branded sample document generated by the DOCX assistant skill.",
        styles: {
            default: {
                document: {
                    run: { font: fontName, size: hp(10.5), color: COLORS.black },
                    paragraph: { spacing: { after: twipFromPt(6), line: twipFromPt(13.5) } },
                },
            },
            paragraphStyles: [
                { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: COVER_FONT, size: hp(28), color: COLORS.black, bold: false }, paragraph: { spacing: { before: 0, after: twipFromPt(6) }, border: TITLE_PARAGRAPH_BORDER } },
                { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: COVER_FONT, size: hp(19), color: COLORS.black, bold: false }, paragraph: { spacing: { before: twipFromPt(8), after: twipFromPt(4) }, outlineLevel: 0, keepNext: true, border: INVISIBLE_HEADING_BORDER } },
                { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: COVER_FONT, size: hp(15), color: COLORS.black, bold: false }, paragraph: { spacing: { before: twipFromPt(5), after: twipFromPt(3) }, outlineLevel: 1, keepNext: true, border: INVISIBLE_HEADING_BORDER } },
                { id: "DocxKicker", name: "DOCX Kicker", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: COVER_FONT, size: hp(14), color: COLORS.blue, bold: false }, paragraph: { spacing: { before: 0, after: twipFromPt(2) }, keepNext: true, border: INVISIBLE_HEADING_BORDER } },
                { id: "DocxSubtitle", name: "DOCX Subtitle", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: fontName, size: hp(11.5), color: COLORS.darkGrey, italics: true }, paragraph: { spacing: { before: 0, after: twipFromPt(10) } } },
            ],
        },
        numbering: {
            config: [
                {
                    reference: "docx-bullets",
                    levels: [
                        {
                            level: 0,
                            format: LevelFormat.BULLET,
                            text: "•",
                            alignment: AlignmentType.LEFT,
                            style: {
                                run: { font: fontName, size: hp(10.2), color: COLORS.black },
                                paragraph: { indent: { left: 420, hanging: 220 }, spacing: { before: 0, after: twipFromPt(2.5) } },
                            },
                        },
                    ],
                },
            ],
        },
        sections: [
            { properties: pageProperties, children: options.coverChildren || [] },
            {
                properties: { ...pageProperties, type: SectionType.NEXT_PAGE },
                headers: { default: makeBrandedHeader() },
                footers: { default: makePageNumberFooter(fontName) },
                children: options.bodyChildren || [],
            },
        ],
    });
}

module.exports = {
    COLORS,
    COVER_FONT,
    CONTENT_WIDTH,
    choosePrimaryFont,
    formatTodayLabel,
    hp,
    fitContentWidths,
    makeBodyParagraph,
    makeBulletedList,
    makeCard,
    makeDataTable,
    makeBrandedCover,
    makeBrandedDocument,
    makeMajorHeading,
    makeMetaBar,
    makePageBreak,
    makeDisplayKicker,
    makePageContextLabel,
    makeSectionOpening,
    makeSubheading,
    makeLogoPlate,
    spacer,
    twipFromPt,
};
