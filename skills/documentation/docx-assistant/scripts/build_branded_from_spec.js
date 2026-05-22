#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { Packer } = require("docx");
const {
    COLORS,
    COVER_FONT,
    choosePrimaryFont,
    formatTodayLabel,
    makeBodyParagraph,
    makeBrandedCover,
    makeBrandedDocument,
    makeBulletedList,
    makeDataTable,
    makePageBreak,
    makeSectionOpening,
    makeSubheading,
    spacer,
    twipFromPt,
} = require("./document_primitives");
const { makeCueBlock } = require("./rich_blocks");

const ROOT = path.resolve(__dirname, "..");
const DEFAULT_OUTPUT = path.join(ROOT, "output", "branded-from-spec.docx");

const CALLOUT_VARIANTS = {
    note: "keyInfo",
    key_info: "keyInfo",
    tip: "tip",
    warning: "warning",
    takeaway: "takeaway",
};

function assertScalar(value, pathLabel) {
    if (value !== undefined && typeof value !== "string") {
        throw new TypeError(`${pathLabel} must be a string`);
    }
}

function buildCover(spec, fontName) {
    const style = spec.style || {};
    if (style.cover === "none") {
        return [];
    }
    const subtitle = spec.subtitle || [spec.customer, spec.date_label || formatTodayLabel()].filter(Boolean).join(" | ");
    return makeBrandedCover({
        bodyFontName: fontName,
        eyebrow: spec.customer ? "Prepared document" : "Branded document",
        title: spec.title,
        subtitle,
        introBody: [],
        cue: null,
        summaryRows: [],
    });
}

function renderCallout(fontName, block) {
    const variant = CALLOUT_VARIANTS[block.variant];
    if (!variant) {
        throw new Error(`Unsupported callout variant: ${block.variant}`);
    }
    assertScalar(block.title, "callout.title");
    return makeCueBlock(fontName, variant, block.body, {
        title: block.title,
        bodyItalics: false,
    });
}

function renderTable(fontName, block) {
    const columnCount = block.headers.length;
    for (const [rowIndex, row] of block.rows.entries()) {
        if (row.length !== columnCount) {
            throw new Error(`table.rows[${rowIndex}] has ${row.length} columns; expected ${columnCount}`);
        }
    }
    const widths = new Array(columnCount).fill(Math.floor(9360 / columnCount));
    return makeDataTable(fontName, block.headers, block.rows, widths);
}

function renderBlock(fontName, block) {
    switch (block.type) {
        case "paragraph":
            return [makeBodyParagraph(fontName, block.text, {
                size: 10.4,
                color: block.emphasis === "muted" ? COLORS.darkGrey : COLORS.black,
                bold: block.emphasis === "strong",
                spacing: { before: 0, after: twipFromPt(6), line: twipFromPt(13.8) },
            })];
        case "heading":
            if ((block.level || 1) === 1) {
                return [...makeSectionOpening(fontName, { heading: block.text })];
            }
            return [makeSubheading(COVER_FONT, block.text)];
        case "bullets":
            return makeBulletedList(fontName, block.items, { fontSize: 10.3, spacingAfter: 2.5, lastSpacingAfter: 5 });
        case "section_banner":
            assertScalar(block.label, "section_banner.label");
            assertScalar(block.title, "section_banner.title");
            assertScalar(block.subtitle, "section_banner.subtitle");
            return [
                ...makeSectionOpening(fontName, {
                    kicker: block.label,
                    heading: block.title,
                    intro: block.subtitle,
                    introAfterPt: 5,
                }),
            ];
        case "callout":
            return [renderCallout(fontName, block), spacer(5)];
        case "table":
            return [renderTable(fontName, block), spacer(5)];
        case "page_break":
            return [makePageBreak()];
        case "raw_docx_xml":
            throw new Error("raw_docx_xml is not supported by the branded renderer yet");
        default:
            throw new Error(`Unknown block type: ${block.type}`);
    }
}

function buildDocument(spec) {
    const fontName = choosePrimaryFont();
    const bodyChildren = [];
    for (const block of spec.blocks) {
        bodyChildren.push(...renderBlock(fontName, block));
    }
    return makeBrandedDocument({
        title: spec.title,
        description: "A branded DOCX generated from the JSON spec.",
        bodyFontName: fontName,
        coverChildren: buildCover(spec, fontName),
        bodyChildren,
    });
}

function parseArgs(argv) {
    const args = { output: DEFAULT_OUTPUT };
    for (let index = 2; index < argv.length; index += 1) {
        const token = argv[index];
        if (token === "--input" && argv[index + 1]) {
            args.input = path.resolve(argv[index + 1]);
            index += 1;
            continue;
        }
        if (token === "--output" && argv[index + 1]) {
            args.output = path.resolve(argv[index + 1]);
            index += 1;
            continue;
        }
        if (token === "--help" || token === "-h") {
            console.log("Usage: node scripts/build_branded_from_spec.js --input spec.json [--output output.docx]");
            process.exit(0);
        }
        throw new Error(`Unknown argument: ${token}`);
    }
    if (!args.input) {
        throw new Error("--input is required");
    }
    return args;
}

async function main() {
    const args = parseArgs(process.argv);
    const spec = JSON.parse(fs.readFileSync(args.input, "utf8"));
    const document = buildDocument(spec);
    const buffer = await Packer.toBuffer(document);
    fs.mkdirSync(path.dirname(args.output), { recursive: true });
    fs.writeFileSync(args.output, buffer);
    console.log(args.output);
}

main().catch((error) => {
    console.error(error.stack || String(error));
    process.exit(1);
});
