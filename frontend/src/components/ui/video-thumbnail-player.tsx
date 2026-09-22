import * as React from "react";
import { Play, X } from "lucide-react";

import { cn } from "@/lib/utils";

// A DOCURA-styled explainer-video surface, adapted from the 21st.dev "Video Thumbnail Player"
// pattern (ravikatiyar162) and reskinned to the Deep Navy + Lime system. Two states:
//
//   • No `videoSrc` (default)  → a clean, non-interactive PLACEHOLDER. Nothing is faked: there
//     is no stock clip, no dummy thumbnail, no modal. It reads as "a video will live here".
//   • `videoSrc` set           → a clickable thumbnail with a lime play control that opens the
//     video in a modal (an <iframe> for an embed URL such as a YouTube/Vimeo embed).
//
// To ship the real video later, set a single value — the `videoSrc` prop (see EXTENSION_VIDEO_SRC
// in the Overview page). No layout or restyle is required.
interface VideoThumbnailPlayerProps extends React.HTMLAttributes<HTMLDivElement> {
  /** The swappable slot. Empty string / undefined renders the placeholder. An embed URL renders a player. */
  videoSrc?: string;
  /** Optional poster image shown behind the play control once a source exists. */
  poster?: string;
  /** Accessible title for the video (used on the play control and iframe). */
  title: string;
  /** Small mono caption shown on the placeholder, e.g. "Explainer · coming soon". */
  placeholderLabel?: string;
  aspectRatio?: "16/9" | "4/3" | "1/1";
}

const VideoThumbnailPlayer = React.forwardRef<HTMLDivElement, VideoThumbnailPlayerProps>(
  (
    { className, videoSrc, poster, title, placeholderLabel = "Explainer · coming soon", aspectRatio = "16/9", ...props },
    ref,
  ) => {
    const [open, setOpen] = React.useState(false);
    const closeRef = React.useRef<HTMLButtonElement>(null);
    const hasVideo = Boolean(videoSrc && videoSrc.trim());

    React.useEffect(() => {
      if (!open) return;
      const onEsc = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
      window.addEventListener("keydown", onEsc);
      const prevOverflow = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      closeRef.current?.focus();
      return () => {
        window.removeEventListener("keydown", onEsc);
        document.body.style.overflow = prevOverflow;
      };
    }, [open]);

    // -- Placeholder state: real, honest "empty" treatment (no fake media). ------------------
    if (!hasVideo) {
      return (
        <div
          ref={ref}
          role="img"
          aria-label={`${title} — video placeholder`}
          className={cn(
            "relative flex flex-col items-center justify-center gap-4 overflow-hidden rounded-md border border-dashed border-border bg-surface/60 text-center",
            className,
          )}
          style={{ aspectRatio }}
          {...props}
        >
          {/* Soft, single lime wash — restrained, no glow spam. */}
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(60%_60%_at_50%_35%,hsl(var(--accent)/0.08),transparent_70%)]" />
          <div className="relative flex size-16 items-center justify-center rounded-full border border-accent/40 bg-accent-soft sm:size-20">
            <Play className="size-7 fill-accent text-accent sm:size-8" aria-hidden />
          </div>
          <div className="relative px-6">
            <p className="label-system">{placeholderLabel}</p>
            <p className="mt-2 max-w-md text-sm text-muted-foreground">
              A short walkthrough of the DOCURA browser extension will appear here.
            </p>
          </div>
        </div>
      );
    }

    // -- Player state: clickable thumbnail → modal iframe. -----------------------------------
    return (
      <>
        <button
          type="button"
          className={cn(
            "group relative block w-full cursor-pointer overflow-hidden rounded-md border border-border bg-surface outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-bg",
            className,
          )}
          style={{ aspectRatio }}
          onClick={() => setOpen(true)}
          aria-label={`Play video: ${title}`}
        >
          {poster ? (
            <img
              src={poster}
              alt=""
              className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
            />
          ) : (
            <div className="absolute inset-0 bg-[radial-gradient(70%_70%_at_50%_30%,hsl(var(--accent)/0.10),transparent_70%)]" />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-bg/70 to-transparent" />
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="flex size-16 items-center justify-center rounded-full border border-accent/50 bg-accent-soft backdrop-blur-sm transition-all duration-300 group-hover:scale-110 sm:size-20">
              <Play className="size-7 fill-accent text-accent sm:size-8" aria-hidden />
            </span>
          </div>
        </button>

        {open ? (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-bg/85 p-4 backdrop-blur-sm"
            role="dialog"
            aria-modal="true"
            aria-label={title}
            onClick={() => setOpen(false)}
          >
            <button
              ref={closeRef}
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Close video"
              className="absolute right-4 top-4 z-10 rounded-full border border-border bg-shell p-2 text-muted-foreground outline-none transition-colors hover:border-accent hover:text-accent focus-visible:ring-2 focus-visible:ring-ring"
            >
              <X className="size-5" aria-hidden />
            </button>
            <div className="aspect-video w-full max-w-4xl" onClick={(e) => e.stopPropagation()}>
              <iframe
                src={videoSrc}
                title={title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="h-full w-full rounded-md border border-border"
              />
            </div>
          </div>
        ) : null}
      </>
    );
  },
);
VideoThumbnailPlayer.displayName = "VideoThumbnailPlayer";

export { VideoThumbnailPlayer };
