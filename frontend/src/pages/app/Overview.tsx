import { Link } from "react-router-dom";
import {
  Activity,
  ArrowRight,
  CheckCircle2,
  Download,
  Eye,
  FileCheck2,
  FileText,
  FolderOpen,
  GitBranch,
  ListChecks,
  Lock,
  MessageSquare,
  MousePointerClick,
  PackageOpen,
  ScanLine,
  ShieldCheck,
  StopCircle,
  ToggleRight,
  Upload,
  UserSquare,
  type LucideIcon,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { HowItWorks } from "@/components/ui/how-it-works";
import { HyperText } from "@/components/ui/hyper-text";
import { Reveal, RevealItem } from "@/components/ui/scroll-reveal";
import { VideoThumbnailPlayer } from "@/components/ui/video-thumbnail-player";

// -----------------------------------------------------------------------------------------
// DOCURA Overview — the informational landing surface shown after sign-in. It explains what
// DOCURA is and how it works using ONLY capabilities that already exist in the project
// (documents, understanding/provenance, My Record, Activity, form sessions, and the M2/M3
// browser extension). No invented features, pricing, testimonials, stats, or logos.
//
// The section structure adapts patterns surveyed on 21st.dev (dual-CTA hero, bento/feature
// grid, vertical "how it works" timeline, thumbnail video, CTA, navigation footer), all
// re-implemented with DOCURA's Deep Navy + Lime tokens for one coherent design.
// -----------------------------------------------------------------------------------------

// ▼▼▼ REPLACE-ME: set this to your extension explainer video's EMBED url (e.g. a YouTube/Vimeo
// "embed" URL) when it is ready. While it is an empty string, a clean placeholder renders and
// nothing is faked. This is the only change needed to ship the real video. ▼▼▼
const EXTENSION_VIDEO_SRC = "/videos/docura-extension-demo.mp4";

const CONTENT_WIDTH = "mx-auto w-full max-w-6xl px-4 sm:px-6";

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <p className="label-system">{children}</p>;
}

function SectionHeading({
  label,
  title,
  lead,
  className = "",
}: {
  label: string;
  title: string;
  lead?: string;
  className?: string;
}) {
  return (
    <div className={`max-w-2xl ${className}`}>
      <SectionLabel>{label}</SectionLabel>
      <h2 className="mt-3 text-balance text-2xl font-bold tracking-tight text-foreground sm:text-3xl">{title}</h2>
      {lead ? <p className="mt-3 text-pretty text-sm leading-relaxed text-muted-foreground sm:text-base">{lead}</p> : null}
    </div>
  );
}

interface Feature {
  icon: LucideIcon;
  title: string;
  body: string;
}

function FeatureCard({ icon: Icon, title, body }: Feature) {
  return (
    <div className="group h-full rounded-md border border-border bg-surface/70 p-5 transition-colors hover:border-accent/40 hover:bg-surface">
      <span className="flex size-9 items-center justify-center rounded-md border border-border bg-surface-2 text-muted-foreground transition-colors group-hover:border-accent/40 group-hover:text-accent">
        <Icon className="size-4" aria-hidden />
      </span>
      <h3 className="mt-4 text-base font-semibold text-foreground">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{body}</p>
    </div>
  );
}

// ---- Section data (all grounded in real project capabilities) ---------------------------

const WHAT_IS: Feature[] = [
  {
    icon: ScanLine,
    title: "Understands documents",
    body: "Upload a document to the vault and DOCURA reads it, extracting details with a confidence level and a link back to the source it came from.",
  },
  {
    icon: UserSquare,
    title: "Builds your record",
    body: "Extracted details assemble into My Record — a structured view of your information that you can inspect and correct.",
  },
  {
    icon: FileCheck2,
    title: "Helps with forms",
    body: "When you work on a form or application, DOCURA prepares and reviews fields using your record, so you are not copying the same details by hand.",
  },
  {
    icon: ShieldCheck,
    title: "You stay in control",
    body: "DOCURA uses only what you authorize. Sensitive disclosures are held back for your explicit approval before they are ever used.",
  },
];

interface Step {
  n: string;
  icon: LucideIcon;
  title: string;
  body: string;
}

const STEPS: Step[] = [
  {
    n: "01",
    icon: Upload,
    title: "Upload your documents",
    body: "Add documents to the vault. They are stored privately and only ever addressed by an opaque key.",
  },
  {
    n: "02",
    icon: ScanLine,
    title: "DOCURA understands them",
    body: "Each document is processed into structured details, each carrying its confidence and the source passage it was drawn from.",
  },
  {
    n: "03",
    icon: UserSquare,
    title: "Your record takes shape",
    body: "Details come together in My Record. You can review provenance, resolve conflicts, and make corrections.",
  },
  {
    n: "04",
    icon: MessageSquare,
    title: "Ask, or start a form",
    body: "Ask DOCURA about your information in the chat workspace, or begin a form session for an application you are completing.",
  },
  {
    n: "05",
    icon: CheckCircle2,
    title: "Review and approve",
    body: "DOCURA checks readiness, matches your details to fields, and hands the form back to you — with sensitive items gated behind your approval.",
  },
];

const CAPABILITIES: { icon: LucideIcon; title: string; body: string; to: string; cta: string }[] = [
  {
    icon: MessageSquare,
    title: "Ask",
    body: "Ask DOCURA about your documents and record in a chat workspace driven by your own information.",
    to: "/ask",
    cta: "Open Ask",
  },
  {
    icon: FileText,
    title: "Documents",
    body: "Upload, track processing status, and open any document to see what DOCURA understood and where it came from.",
    to: "/documents",
    cta: "Open Documents",
  },
  {
    icon: UserSquare,
    title: "My Record",
    body: "See your structured record assembled from your documents, with provenance and the ability to correct it.",
    to: "/record",
    cta: "Open My Record",
  },
  {
    icon: Activity,
    title: "Activity",
    body: "Review a timeline of what happened across your form sessions — fills, selections, attachments, approvals and hand-backs.",
    to: "/activity",
    cta: "Open Activity",
  },
];

const EXTENSION_POINTS: Feature[] = [
  {
    icon: MousePointerClick,
    title: "Activates only when you choose",
    body: "Nothing runs on a page passively. The extension starts a form session and shows an indicator only when you explicitly activate it on the current tab.",
  },
  {
    icon: Eye,
    title: "A visible active indicator",
    body: "While active, a persistent indicator makes it clear the session is running — there is no hidden background activity.",
  },
  {
    icon: StopCircle,
    title: "You can stop it anytime",
    body: "Stopping ends the session and removes the indicator. Values already on the page are left untouched.",
  },
  {
    icon: Lock,
    title: "Careful with your data",
    body: "The sign-in token lives only in memory for the session, never on disk, and is not reachable by the pages you visit.",
  },
];

// The extension is distributed as an unpacked ZIP loaded in Developer Mode (M2/M3), so the
// install path is: download → extract → enable Developer Mode → load unpacked → use.
const EXTENSION_INSTALL: { icon: LucideIcon; title: string; body: string }[] = [
  { icon: Download, title: "Download extension", body: "Download the DOCURA browser extension ZIP." },
  { icon: FolderOpen, title: "Extract the ZIP", body: "Extract the downloaded ZIP file to a folder on your computer." },
  { icon: ToggleRight, title: "Enable Developer Mode", body: "Open your browser's Extensions page and enable Developer Mode." },
  { icon: PackageOpen, title: "Load unpacked", body: 'Click "Load unpacked" and select the extracted DOCURA extension folder.' },
  { icon: CheckCircle2, title: "Use DOCURA", body: "Open a supported web form and use the DOCURA extension to access relevant information for filling the form." },
];

const FORM_LIFECYCLE: { icon: LucideIcon; title: string; body: string }[] = [
  { icon: ListChecks, title: "Readiness", body: "What the form needs before it can continue." },
  { icon: GitBranch, title: "Matching", body: "Your details lined up against the form's fields." },
  { icon: Eye, title: "Review", body: "You see the proposed fields before anything is final." },
  { icon: ShieldCheck, title: "Approval", body: "Sensitive disclosures wait for your explicit yes." },
  { icon: ArrowRight, title: "Hand-back", body: "The form returns to you — DOCURA never submits it for you." },
];

const CONTROLS: Feature[] = [
  {
    icon: ShieldCheck,
    title: "You authorize what is used",
    body: "DOCURA works from your record, and sensitive disclosures require your explicit approval before they are applied to a form.",
  },
  {
    icon: Eye,
    title: "Every detail shows its source",
    body: "Extracted information carries its confidence and a link to the document passage it came from, so you can check it.",
  },
  {
    icon: FileCheck2,
    title: "Corrections are yours to make",
    body: "Where DOCURA is unsure or wrong, you can correct your record — your input is the source of truth.",
  },
];

// ---- The page ----------------------------------------------------------------------------

export default function OverviewPage() {
  return (
    <div className="pb-4 text-foreground">
      {/* 1 · HERO ------------------------------------------------------------------------- */}
      <section className="relative overflow-hidden border-b border-border">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(60%_50%_at_50%_0%,hsl(var(--accent)/0.08),transparent_70%)]" />
        <div className={`${CONTENT_WIDTH} relative py-16 sm:py-24`}>
          <Reveal stagger onMount className="mx-auto max-w-3xl text-center">
            {/* Brand lockup: DOCURA (animated wordmark) with the tagline directly beneath it. The
                scramble animation is scoped to the HyperText word only; nothing else here moves. */}
            <RevealItem>
              <div className="flex justify-center">
                <HyperText
                  text="DOCURA"
                  className="text-5xl font-bold leading-none tracking-tight text-foreground sm:text-6xl"
                />
              </div>
              <p className="label-system mt-1">Personal document intelligence</p>
            </RevealItem>
            <RevealItem>
              <h1 className="mt-6 text-balance text-3xl font-bold leading-tight tracking-tight text-foreground sm:text-5xl">
                Understand your documents.{" "}
                <span className="text-accent">Fill forms with confidence.</span>
              </h1>
            </RevealItem>
            <RevealItem>
              <p className="mx-auto mt-5 max-w-2xl text-pretty text-base leading-relaxed text-muted-foreground sm:text-lg">
                DOCURA reads the documents you upload, turns them into a structured record you
                control, and helps you complete forms and applications using only the information
                you authorize.
              </p>
            </RevealItem>
            <RevealItem className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
              <Button asChild>
                <Link to="/ask">
                  Ask DOCURA <ArrowRight className="size-4" aria-hidden />
                </Link>
              </Button>
              <Button asChild variant="outline">
                <Link to="/documents">View documents</Link>
              </Button>
            </RevealItem>
          </Reveal>
        </div>
      </section>

      {/* 2 · WHAT IS DOCURA --------------------------------------------------------------- */}
      <section className={`${CONTENT_WIDTH} py-16 sm:py-20`}>
        <Reveal>
          <SectionHeading
            label="What is DOCURA"
            title="A layer of understanding over your own documents"
            lead="DOCURA is not a place to store files and forget them. It reads what you give it, keeps track of where each detail came from, and puts that understanding to work when you need it."
          />
        </Reveal>
        <Reveal stagger className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {WHAT_IS.map((f) => (
            <RevealItem key={f.title} className="h-full">
              <FeatureCard {...f} />
            </RevealItem>
          ))}
        </Reveal>
      </section>

      {/* 3 · HOW DOCURA WORKS (floating-card timeline) ------------------------------------ */}
      <section className="border-y border-border bg-surface/30">
        <div className={`${CONTENT_WIDTH} py-16 sm:py-20`}>
          <Reveal>
            <SectionHeading label="How it works" title="From documents to a completed form" />
          </Reveal>
          {/* Floating pinned-card timeline (21st.dev "how-it-works", re-themed to DOCURA). The
              step content is unchanged; only the presentation moved from the vertical list. */}
          <div className="mt-12">
            <HowItWorks
              steps={STEPS.map((step) => ({
                title: step.title,
                description: step.body,
                icon: step.icon,
              }))}
            />
          </div>
        </div>
      </section>

      {/* 4 · DOCUMENTS + FORMS (bento) ---------------------------------------------------- */}
      <section className={`${CONTENT_WIDTH} py-16 sm:py-20`}>
        <Reveal>
          <SectionHeading
            label="Documents & forms"
            title="What DOCURA works with"
            lead="Two things move through DOCURA: the documents you upload, and the forms you are trying to complete. The record in the middle connects them."
          />
        </Reveal>
        <Reveal className="mt-10 grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="rounded-md border border-border bg-surface/70 p-6 lg:row-span-2 lg:flex lg:flex-col">
            <span className="flex size-9 items-center justify-center rounded-md border border-border bg-surface-2 text-accent">
              <FileText className="size-4" aria-hidden />
            </span>
            <h3 className="mt-4 text-lg font-semibold text-foreground">Documents</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              Upload documents to a private vault and watch their processing status. Open any one
              to see exactly what DOCURA understood, with a confidence level and a link to the
              source passage behind each detail.
            </p>
            <div className="mt-5 flex flex-wrap gap-2 lg:mt-auto">
              {["Upload", "Processing status", "Understanding", "Provenance"].map((t) => (
                <span key={t} className="rounded border border-border bg-surface-2 px-2.5 py-1 text-xs text-muted-foreground">
                  {t}
                </span>
              ))}
            </div>
          </div>
          <div className="rounded-md border border-border bg-surface/70 p-6">
            <span className="flex size-9 items-center justify-center rounded-md border border-border bg-surface-2 text-accent">
              <UserSquare className="size-4" aria-hidden />
            </span>
            <h3 className="mt-4 text-base font-semibold text-foreground">My Record</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              A structured record assembled from your documents — attributes you can review,
              trace to their source, and correct when needed.
            </p>
          </div>
          <div className="rounded-md border border-border bg-surface/70 p-6">
            <span className="flex size-9 items-center justify-center rounded-md border border-border bg-surface-2 text-accent">
              <FileCheck2 className="size-4" aria-hidden />
            </span>
            <h3 className="mt-4 text-base font-semibold text-foreground">Forms & applications</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              A form session checks readiness, matches your details to fields, and hands the form
              back to you for review — never submitting anything on your behalf.
            </p>
          </div>
        </Reveal>
      </section>

      {/* 5 · BROWSER EXTENSION ------------------------------------------------------------ */}
      <section className="border-y border-border bg-surface/30">
        <div className={`${CONTENT_WIDTH} py-16 sm:py-20`}>
          <div className="grid grid-cols-1 gap-10 lg:grid-cols-2 lg:items-start">
            <Reveal>
              <SectionHeading
                label="Browser extension"
                title="DOCURA where the form actually lives"
                lead="The DOCURA browser extension brings your record to the page you are filling in — on your terms. It is built so that control and privacy hold by construction, not by a setting you have to remember."
              />
            </Reveal>
            <Reveal stagger className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {EXTENSION_POINTS.map((f) => (
                <RevealItem key={f.title} className="h-full">
                  <FeatureCard {...f} />
                </RevealItem>
              ))}
            </Reveal>
          </div>
        </div>
      </section>

      {/* 6 · EXTENSION EXPLAINER VIDEO ---------------------------------------------------- */}
      <section className={`${CONTENT_WIDTH} py-16 sm:py-20`}>
        <Reveal>
          <SectionHeading
            label="Watch"
            title="How the DOCURA extension works"
            lead="A short walkthrough of activating the extension, reading a form, and handing it back — coming soon."
            className="mx-auto text-center"
          />
        </Reveal>
        <Reveal className="mx-auto mt-10 max-w-4xl">
          <VideoThumbnailPlayer
            videoSrc={EXTENSION_VIDEO_SRC}
            title="How the DOCURA extension works"
            placeholderLabel="Extension walkthrough · coming soon"
          />
        </Reveal>
      </section>

      {/* 6.5 · EXTENSION DOWNLOAD & INSTALL ------------------------------------------------ */}
      <section className="border-y border-border bg-surface/30">
        <div className={`${CONTENT_WIDTH} py-16 sm:py-20`}>
          <Reveal>
            <SectionHeading
              label="Get the extension"
              title="DOCURA Browser Extension"
              lead="Use the DOCURA browser extension to access your stored document information while filling supported web forms."
            />
          </Reveal>
          <Reveal as="ol" stagger className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {EXTENSION_INSTALL.map((step, i) => (
              <RevealItem as="li" key={step.title} className="rounded-md border border-border bg-shell/60 p-5">
                <div className="flex items-center justify-between">
                  <span className="flex size-9 items-center justify-center rounded-md border border-border bg-surface-2 text-accent">
                    <step.icon className="size-4" aria-hidden />
                  </span>
                  <span className="font-mono text-xs text-muted-foreground">{`0${i + 1}`}</span>
                </div>
                <h3 className="mt-4 text-sm font-semibold text-foreground">{step.title}</h3>
                <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">{step.body}</p>
              </RevealItem>
            ))}
          </Reveal>
          <Reveal className="mt-10 flex flex-col items-center gap-4 text-center">
            <Button asChild>
              <a href="/downloads/docura-extension.zip" download>
                <Download className="size-4" aria-hidden /> Download Extension
              </a>
            </Button>
            <p className="max-w-xl text-sm leading-relaxed text-muted-foreground">
              Review the information before using it. DOCURA does not submit the form on your behalf.
            </p>
          </Reveal>
        </div>
      </section>

      {/* 7 · FORM-SESSION JOURNEY (horizontal stepper) ------------------------------------ */}
      <section className="border-y border-border bg-surface/30">
        <div className={`${CONTENT_WIDTH} py-16 sm:py-20`}>
          <Reveal>
            <SectionHeading
              label="The journey"
              title="How a form session flows"
              lead="Every form session moves through the same stages — always ending back in your hands."
            />
          </Reveal>
          <Reveal as="ol" stagger className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {FORM_LIFECYCLE.map((stage, i) => (
              <RevealItem as="li" key={stage.title} className="rounded-md border border-border bg-shell/60 p-5">
                <div className="flex items-center justify-between">
                  <span className="flex size-9 items-center justify-center rounded-md border border-border bg-surface-2 text-accent">
                    <stage.icon className="size-4" aria-hidden />
                  </span>
                  <span className="font-mono text-xs text-muted-foreground">{`0${i + 1}`}</span>
                </div>
                <h3 className="mt-4 text-sm font-semibold text-foreground">{stage.title}</h3>
                <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">{stage.body}</p>
              </RevealItem>
            ))}
          </Reveal>
        </div>
      </section>

      {/* 8 · WHAT YOU CAN DO -------------------------------------------------------------- */}
      <section className={`${CONTENT_WIDTH} py-16 sm:py-20`}>
        <Reveal>
          <SectionHeading label="Inside DOCURA" title="What you can do" />
        </Reveal>
        <Reveal stagger className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {CAPABILITIES.map((c) => (
            <RevealItem key={c.title} className="flex flex-col rounded-md border border-border bg-surface/70 p-6">
              <div className="flex items-start gap-4">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-md border border-border bg-surface-2 text-accent">
                  <c.icon className="size-4" aria-hidden />
                </span>
                <div>
                  <h3 className="text-base font-semibold text-foreground">{c.title}</h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{c.body}</p>
                </div>
              </div>
              <Link
                to={c.to}
                className="mt-4 inline-flex items-center gap-1.5 self-start font-mono text-xs font-bold uppercase tracking-system text-accent outline-none transition-colors hover:text-accent-hover focus-visible:underline"
              >
                {c.cta} <ArrowRight className="size-3.5" aria-hidden />
              </Link>
            </RevealItem>
          ))}
        </Reveal>
      </section>

      {/* 9 · USER CONTROL / SAFETY -------------------------------------------------------- */}
      <section className="border-y border-border bg-surface/30">
        <div className={`${CONTENT_WIDTH} py-16 sm:py-20`}>
          <Reveal>
            <SectionHeading
              label="Control & authorization"
              title="Your information, on your terms"
              lead="DOCURA is built around your authorization. These are concrete behaviours in the product — not promises."
            />
          </Reveal>
          <Reveal stagger className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {CONTROLS.map((f) => (
              <RevealItem key={f.title} className="h-full">
                <FeatureCard {...f} />
              </RevealItem>
            ))}
          </Reveal>
        </div>
      </section>

      {/* 10 · CTA ------------------------------------------------------------------------- */}
      <section className={`${CONTENT_WIDTH} py-16 sm:py-24`}>
        <Reveal className="relative overflow-hidden rounded-md border border-accent/30 bg-surface/70 px-6 py-12 text-center sm:px-12 sm:py-16">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(60%_80%_at_50%_0%,hsl(var(--accent)/0.10),transparent_70%)]" />
          <div className="relative">
            <h2 className="text-balance text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
              Pick up where your documents leave off
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-muted-foreground sm:text-base">
              Ask DOCURA about your record, or head to your documents to add more.
            </p>
            <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
              <Button asChild>
                <Link to="/ask">
                  Ask DOCURA <ArrowRight className="size-4" aria-hidden />
                </Link>
              </Button>
              <Button asChild variant="outline">
                <Link to="/documents">Go to documents</Link>
              </Button>
            </div>
          </div>
        </Reveal>
      </section>

      {/* 11 · FOOTER ---------------------------------------------------------------------- */}
      <footer className="border-t border-border">
        <Reveal className={`${CONTENT_WIDTH} flex flex-col items-center justify-between gap-6 py-10 sm:flex-row`}>
          <div className="flex items-center gap-2">
            <span className="flex size-6 items-center justify-center rounded-md bg-accent">
              <MessageSquare className="size-3.5 text-accent-foreground" aria-hidden />
            </span>
            <span className="text-sm font-bold tracking-tight text-foreground">DOCURA</span>
          </div>
          <nav aria-label="Footer" className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
            {[
              { to: "/overview", label: "Overview" },
              { to: "/ask", label: "Ask" },
              { to: "/documents", label: "Documents" },
              { to: "/record", label: "My Record" },
              { to: "/activity", label: "Activity" },
            ].map((l) => (
              <Link
                key={l.to}
                to={l.to}
                className="text-sm text-muted-foreground outline-none transition-colors hover:text-foreground focus-visible:text-foreground"
              >
                {l.label}
              </Link>
            ))}
          </nav>
          <p className="text-xs text-muted-foreground">Personal document intelligence</p>
        </Reveal>
      </footer>
    </div>
  );
}
