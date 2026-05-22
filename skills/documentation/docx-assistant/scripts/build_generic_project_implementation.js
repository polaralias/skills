#!/usr/bin/env node
"use strict";

// Thin implementation-plan specialization over the shared branded DOCX shell.

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
    makeCueBlock,
    makeKeyInfoCue,
    makeTakeawayCue,
    makeTipCue,
    makeWarningCue,
} = require("./rich_blocks");

const ROOT = path.resolve(__dirname, "..");
const DEFAULT_OUTPUT = path.join(ROOT, "output", "generic-project-implementation.docx");
const DEFAULT_TITLE = "Standard implementation plan";

function buildCover(customerName, todayLabel, bodyFontName) {
    return makeBrandedCover({
        bodyFontName,
        eyebrow: "Project implementation",
        title: DEFAULT_TITLE,
        subtitle: `${customerName} | ${todayLabel}`,
        introBody: [
            "This sample shows how the shared DOCX system can carry an implementation-plan narrative without falling back to a flat office-template layout.",
            "It keeps the cover, running chrome, section framing, and semantic panel language aligned with the richer branded baseline.",
        ],
        cue: {
            label: "LAYOUT",
            title: "Why this layout works",
            body: [
        "The first page combines a strong title hierarchy with calm accents and a neutral surface, so the document feels branded without becoming noisy.",
                "The summary table and labelled cue create scanability before the document moves into denser delivery detail.",
            ],
        },
        summaryRows: [
            ["Use case", "Customer-facing implementation plans, rollout packs, mobilisation notes, and delivery working documents."],
            ["Shared baseline", "Protected logo treatment, display-led hierarchy, page-context kickers, metadata bars, and semantic cue panels."],
            ["Implementation focus", "Discovery, configuration, launch readiness, training, governance, and early adoption review."],
            ["Delivery gate", "Keep the shared DOCX packaging rules, then swap only the customer-specific content and workstreams."],
        ],
    });
}

function buildBody(bodyFontName) {
    return [
        ...makeSectionOpening(bodyFontName, {
            kicker: "Implementation phase",
            heading: "Discovery and solution alignment",
            meta: {
                leftLabel: "Focus",
                leftValue: "Scope, governance, and solution decisions",
                rightLabel: "Indicative duration",
                rightValue: "3 to 4 weeks",
            },
            intro: "The discovery phase confirms scope, clarifies delivery ownership, and aligns the learning design, governance, and data approach before build work accelerates.",
        }),
        makeWarningCue(
            bodyFontName,
            "The customer should name a project sponsor, a day-to-day administrator, and the key subject matter owners needed for discovery, validation, launch, and post-launch support.",
            { title: "Critical dependency" },
        ),
        spacer(5),
        makeDataTable(
            bodyFontName,
            ["Phase", "Focus", "Indicative duration", "Key outputs"],
            [
                ["1. Mobilise", "Kickoff, scope confirmation, governance, success measures", "1 week", "Plan, RAID log, stakeholder map"],
                ["2. Discover", "Platform decisions, content shape, integrations, security, reporting", "2 weeks", "Solution notes, dependencies, content inventory"],
                ["3. Validate", "Sign-off on approach, roles, and launch sequence", "1 week", "Validated configuration decisions and launch path"],
            ],
            [1500, 3150, 1700, 3010],
        ),
        spacer(5),
        makeKeyInfoCue(
            bodyFontName,
            "Use short labelled cue blocks to surface owners, risks, and decisions before readers reach denser workstream detail or tables.",
            { title: "Scanability pattern" },
        ),
        spacer(7),
        makeSubheading(COVER_FONT, "Discovery workstreams"),
        makeBodyParagraph(bodyFontName, "These workstreams separate the main delivery themes so decisions stay visible without collapsing the page into one dense block.", {
            size: 10.2,
            color: COLORS.darkGrey,
            spacing: { before: 0, after: twipFromPt(5), line: twipFromPt(13.5) },
        }),
        makeCard(bodyFontName, "Platform setup and governance", [
            "Confirm tenancy, security expectations, branding requirements, and user-administration ownership.",
            "Map the learning lifecycle: authoring, approval, enrolment, completion, and reporting.",
            "Agree the initial decision log so open points are surfaced early.",
        ], "neutral"),
        spacer(4),
        makeCard(bodyFontName, "Content and experience design", [
            "Review priority programmes, learner groups, accessibility needs, and assessment patterns.",
            "Identify where richer guidance panels, worked examples, and quick-reference layouts will help users scan faster.",
        ], "example"),
        spacer(4),
        makeCard(bodyFontName, "Data, launch, and support model", [
            "Define the reporting outcomes that matter to leadership, administrators, and customer success teams.",
            "Agree escalation routes, support ownership, and launch-readiness checkpoints before training is scheduled.",
        ], "neutral"),
        makePageBreak(),
        ...makeSectionOpening(bodyFontName, {
            kicker: "Operational readiness",
            heading: "Configuration, launch readiness, and training",
            meta: {
                leftLabel: "Focus",
                leftValue: "Build, launch readiness, training, and handover",
                rightLabel: "Indicative duration",
                rightValue: "4 to 6 weeks",
            },
            intro: "Once discovery decisions are settled, the delivery shifts into configuration, content assembly, launch controls, and practical enablement for the teams who will run the platform day to day.",
        }),
        makeTakeawayCue(
            bodyFontName,
            [
                "Administrators can complete their core workflows without external support.",
                "Learner-facing journeys are tested with real examples before launch communications go out.",
                "Training materials mirror the final configured platform rather than a generic demo environment.",
            ],
            { title: "What good looks like" },
        ),
        spacer(6),
        makeSubheading(COVER_FONT, "Training and handover priorities"),
        ...makeBulletedList(bodyFontName, [
            "Administrator training should be scenario-led, not just feature-led.",
            "Launch materials should include comms timing, support channels, and early-adoption feedback loops.",
            "Handover should leave the customer with clear ownership for reporting, content updates, and future iteration.",
        ], {
            fontSize: 10.3,
            spacingAfter: 2.5,
            lastSpacingAfter: 4,
        }),
        makeTipCue(
            bodyFontName,
            "Short, clearly labelled note, warning, and takeaway blocks help administrators recover the next step without rereading the whole page.",
            { title: "Training material pattern" },
        ),
        spacer(5),
        makeDataTable(
            bodyFontName,
            ["Workstream", "Owner", "What needs to be ready"],
            [
                ["Configuration", "Implementation lead", "Roles, branding, navigation, learner journeys, baseline reporting"],
                ["Content", "Customer content owners", "Initial learning set, quality checks, media approvals, accessibility review"],
                ["Training", "Delivery team + customer admins", "Admin sessions, quick guides, scenario practice, support model"],
                ["Launch", "Project sponsor + admins", "Communications, go-live checklist, issue path, success measures"],
            ],
            [1850, 1850, 5660],
        ),
        spacer(6),
        makeKeyInfoCue(
            bodyFontName,
            "Richer DOCX styling is only shippable once the rendered pages are checked for spacing, page breaks, table integrity, and logo placement. Review mechanics like comments need structural checks too.",
            { title: "Render-first QA reminder" },
        ),
        makePageBreak(),
        ...makeSectionOpening(bodyFontName, {
            kicker: "Governance and improvement",
            heading: "Governance, adoption, and next steps",
            meta: {
                leftLabel: "Focus",
                leftValue: "Adoption, governance, and improvement planning",
                rightLabel: "Review window",
                rightValue: "First 90 days",
            },
            intro: "The best implementation plans do not stop at launch. They define how progress is reviewed, where adoption signals are captured, and how the customer team keeps improving the platform after go-live.",
        }),
        makeCueBlock(
            bodyFontName,
            "visual",
            [
                "Weekly during implementation: decisions, blockers, and readiness confidence.",
                "Fortnightly after launch: adoption signals, admin friction points, and content improvement priorities.",
            ],
            {
                label: "CHECKPOINTS",
                title: "Governance rhythm",
                bodyItalics: false,
            },
        ),
        spacer(6),
        makeDataTable(
            bodyFontName,
            ["Timeframe", "Primary outcome", "Measures to check"],
            [
                ["First 30 days", "Smooth launch and confident admins", "Completion rates, support queries, admin confidence"],
                ["First 60 days", "Stable reporting and learner uptake", "Usage trends, stakeholder feedback, quality of data"],
                ["First 90 days", "Adoption review and enhancement backlog", "Repeat engagement, content gaps, roadmap items"],
            ],
            [1800, 3200, 4360],
        ),
        spacer(6),
        makeSubheading(COVER_FONT, "Immediate next steps"),
        makeBodyParagraph(bodyFontName, "Close the document with a short action frame before the final panel so the transition feels deliberate rather than abrupt.", {
            size: 10.2,
            color: COLORS.darkGrey,
            spacing: { before: 0, after: twipFromPt(5), line: twipFromPt(13.5) },
        }),
        makeCard(bodyFontName, "Next actions for this plan", [
            "Confirm customer names, owners, and governance dates.",
            "Replace the generic workstreams with customer-specific deliverables and launch dependencies.",
            "Run the structural validator if comments or review markup are involved, then rerender before delivery.",
        ], "action"),
    ];
}

function buildDocument(customerName) {
    const bodyFontName = choosePrimaryFont();
    const todayLabel = formatTodayLabel();

    return makeBrandedDocument({
        title: DEFAULT_TITLE,
        description: "A branded sample implementation plan generated by the DOCX assistant skill.",
        bodyFontName,
        coverChildren: buildCover(customerName, todayLabel, bodyFontName),
        bodyChildren: buildBody(bodyFontName),
    });
}

function parseArgs(argv) {
    const args = {
        output: DEFAULT_OUTPUT,
        customer: "Example customer",
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
        if (token === "--help" || token === "-h") {
            console.log("Usage: node scripts/build_generic_project_implementation.js [--output PATH] [--customer NAME]");
            process.exit(0);
        }
        throw new Error(`Unknown argument: ${token}`);
    }

    return args;
}

async function main() {
    const args = parseArgs(process.argv);
    const document = buildDocument(args.customer);
    const buffer = await Packer.toBuffer(document);
    fs.mkdirSync(path.dirname(args.output), { recursive: true });
    fs.writeFileSync(args.output, buffer);
    console.log(args.output);
}

main().catch((error) => {
    console.error(error.stack || String(error));
    process.exit(1);
});
