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
    makeCard,
    makeDataTable,
    makePageBreak,
    makeSectionOpening,
    makeSubheading,
    spacer,
    twipFromPt,
} = require("./document_primitives");
const {
    makeKeyInfoCue,
    makeTakeawayCue,
    makeTipCue,
    makeVisualCue,
    makeWarningCue,
} = require("./rich_blocks");

const ROOT = path.resolve(__dirname, "..");
const DEFAULT_OUTPUT = path.join(ROOT, "output", "example-document.docx");

function buildDocument(customerName, documentTitle) {
    const fontName = choosePrimaryFont();
    const todayLabel = formatTodayLabel();
    const coverChildren = makeBrandedCover({
        bodyFontName: fontName,
        eyebrow: "Example document",
        title: documentTitle,
        subtitle: `${customerName} | ${todayLabel}`,
        introBody: [
            "This file is the default visual baseline for new branded DOCX work when the request is not tied to a specific document family.",
            "It shows the shared cover, running chrome, section pacing, and cue-panel language that should travel across reports, explainers, guides, and plans.",
        ],
        cue: {
            label: "SYSTEM",
            title: "Why this sample exists",
            body: [
                "Start here for a branded document that needs strong visual rhythm but does not naturally map to the implementation-plan sample.",
                "Then adapt the content blocks, not the visual grammar, so new outputs still feel recognisably coherent.",
            ],
        },
        summaryRows: [
            ["Use case", "Reports, explainers, handouts, training guides, SOPs, packs, and customer-facing notes."],
            ["Shared assets", "Display-font cover styling, optional cover and header logo treatment, clear headings, and reusable cue blocks."],
            ["Body system", "Metadata bars, intro bridges, coloured panels, structured tables, and closing actions."],
            ["Shipping gate", "Semantic lint, render, visual check, then deliver the final DOCX only."],
        ],
    });

    const bodyChildren = [
        ...makeSectionOpening(fontName, {
            kicker: "Reusable document system",
            heading: "A reusable branded document baseline",
            meta: {
                leftLabel: "Best fit",
                leftValue: "Fresh branded docs without a narrower template",
                rightLabel: "Coverage",
                rightValue: "Multi-purpose",
            },
            intro: "This body layout is intended to be copied into other document families so new outputs inherit the same header, hierarchy, pacing, and panel behaviour by default.",
        }),
        makeVisualCue(fontName, [
            "Open a page with a short label, a strong H1, and a compact metadata bar so the reader knows what the section is for before they hit any dense detail.",
            "Use a short bridge paragraph before the first coloured panel so headings and tinted surfaces do not crash into one another.",
        ], { title: "Default page opening" }),
        spacer(6),
        makeSubheading(COVER_FONT, "Core building blocks"),
        makeBodyParagraph(fontName, "This first section shows the shared blocks that should be mixed according to document intent rather than invented from scratch each time.", {
            size: 10.2,
            color: COLORS.darkGrey,
            spacing: { before: 0, after: twipFromPt(5), line: twipFromPt(13.5) },
        }),
        makeCard(fontName, "What every new branded doc should normally carry", [
            "A clear cover with the logo treatment, strong title styling, and a short framing summary.",
            "A running body header with the configured logo on every page after the cover.",
            "At least one visual anchor per dense page: metadata bar, cue block, card, or structured table.",
        ], "neutral"),
        spacer(4),
        makeKeyInfoCue(fontName, "Cue blocks should change meaning, not just colour. Use each one for a real semantic purpose so the page becomes easier to scan.", { title: "Panel rule" }),
        spacer(4),
        makeWarningCue(fontName, "Do not let short explainers collapse into plain heading-plus-bullets layouts if the document is still meant to feel client-ready and branded.", { title: "Common failure mode" }),
        spacer(6),
        makeDataTable(fontName, ["Block", "Best use", "Why it helps"], [
            ["Metadata bar", "Section framing, ownership, timing, scope", "Adds fast context before narrative starts"],
            ["Visual cue", "Scene-setting, layout explanation, walkthrough framing", "Adds personality without heavy decoration"],
            ["Key info", "Important context or assumptions", "Stops critical framing from disappearing into body copy"],
            ["Warning", "Risks, blockers, governance points", "Signals caution without using loud colours everywhere"],
            ["Tip / takeaway", "Best practice or summary", "Gives the reader a practical or memorable close"],
        ], [1800, 2850, 4710]),
        makePageBreak(),
        ...makeSectionOpening(fontName, {
            kicker: "Section patterns",
            heading: "Section stacks that travel well",
            meta: {
                leftLabel: "Pattern",
                leftValue: "Intro, cue, structure, close",
                rightLabel: "Default",
                rightValue: "Yes",
            },
            intro: "The same visual system can support different document types so long as the section stack stays intentional: opening frame, working detail, supporting callouts, and a clean close.",
        }),
        makeTakeawayCue(fontName, [
            "The implementation-plan sample should be treated as one specialization of the system, not the system itself.",
            "New document types should start from the shared primitives and this example builder, then layer in only the structures they actually need.",
        ], { title: "Recommended default" }),
        spacer(6),
        makeSubheading(COVER_FONT, "Suggested section order"),
        makeBodyParagraph(fontName, "This is a reusable stack for richer pages that need more than plain narrative but should still stay controlled and businesslike.", {
            size: 10.2,
            color: COLORS.darkGrey,
            spacing: { before: 0, after: twipFromPt(5), line: twipFromPt(13.5) },
        }),
        ...makeBulletedList(fontName, [
            "Open with a section label, display H1, and metadata bar.",
            "Add one concise bridge paragraph before the first callout or card.",
            "Use one or two semantic panels to surface the highest-value context.",
            "Bring in a table, checklist, or card when the reader needs structure rather than more prose.",
            "Close with a takeaway, next-step card, or warning depending on the section's job.",
        ], {
            fontSize: 10.3,
            spacingAfter: 2.5,
            lastSpacingAfter: 4,
        }),
        makeTipCue(fontName, "If a page feels flat, add structure before adding decoration. Usually the missing ingredient is a better block sequence, not more colour.", { title: "Design heuristic" }),
        spacer(5),
        makeCard(fontName, "Section endings that usually work well", [
            "Takeaway panels when the reader needs one durable message.",
            "Action cards when the section should end with ownership or next steps.",
            "Warning panels when the close should stop a risky or lazy interpretation.",
        ], "example"),
        spacer(6),
        ...makeSectionOpening(fontName, {
            kicker: "Delivery checks",
            heading: "Delivery rules still apply",
            meta: {
                leftLabel: "Must pass",
                leftValue: "Semantic lint, render, visual review",
                rightLabel: "Header rule",
                rightValue: "Required",
            },
            intro: "This example is only useful if the final DOCX still meets the packaging and QA standards that keep Word happy and the output visually correct.",
        }),
        makeKeyInfoCue(fontName, "The generic example is discoverable on purpose: use it as the baseline for unfamiliar document requests, and use the implementation-plan builder only when the document really is that format.", { title: "How to choose the right builder" }),
    ];

    return makeBrandedDocument({
        title: documentTitle,
        description: "A generic branded example generated by the DOCX assistant skill.",
        bodyFontName: fontName,
        coverChildren,
        bodyChildren,
    });
}

function parseArgs(argv) {
    const args = {
        output: DEFAULT_OUTPUT,
        customer: "Example customer",
        title: "Branded example document",
    };

    for (let index = 2; index < argv.length; index += 1) {
        const token = argv[index];
        if (token === "--output" && argv[index + 1]) {
            args.output = path.resolve(argv[index + 1]);
            index += 1;
            continue;
        }
        if ((token === "--customer" || token === "--customer_name") && argv[index + 1]) {
            args.customer = argv[index + 1];
            index += 1;
            continue;
        }
        if (token === "--title" && argv[index + 1]) {
            args.title = argv[index + 1];
            index += 1;
            continue;
        }
        if (token === "--help" || token === "-h") {
            console.log("Usage: node scripts/build_example_document.js [--output PATH] [--customer NAME] [--title TEXT]");
            process.exit(0);
        }
        throw new Error(`Unknown argument: ${token}`);
    }

    return args;
}

async function main() {
    const args = parseArgs(process.argv);
    const document = buildDocument(args.customer, args.title);
    const buffer = await Packer.toBuffer(document);
    fs.mkdirSync(path.dirname(args.output), { recursive: true });
    fs.writeFileSync(args.output, buffer);
    console.log(args.output);
}

main().catch((error) => {
    console.error(error.stack || String(error));
    process.exit(1);
});
