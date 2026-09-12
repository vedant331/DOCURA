import { useRef, useState, type DragEvent } from "react";
import { UploadCloud } from "lucide-react";

import { cn } from "@/lib/utils";

// Reusable file dropzone (§8). Keyboard- and pointer-accessible: the whole area is a
// button that opens the native picker, and it also accepts drag-and-drop. It only
// collects files — validation and upload are the dialog's job.
export function UploadDropzone({
  onFiles,
  accept,
  disabled,
}: {
  onFiles: (files: File[]) => void;
  accept?: string;
  disabled?: boolean;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const pick = (list: FileList | null) => {
    if (list && list.length) onFiles(Array.from(list));
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    if (disabled) return;
    pick(e.dataTransfer.files);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
    >
      <button
        type="button"
        disabled={disabled}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "flex w-full flex-col items-center justify-center gap-3 border border-dashed px-6 py-12 text-center transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50",
          dragging ? "border-mercury bg-surface" : "border-border bg-surface/30 hover:border-mercury/40",
        )}
        aria-label="Choose files to upload, or drag and drop"
      >
        <UploadCloud className="size-7 text-muted-foreground" aria-hidden />
        <span className="text-sm text-foreground">
          {dragging ? "Drop to add" : "Drag files here, or click to choose"}
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted-foreground">
          PDF · JPG · PNG
        </span>
      </button>
      <input
        ref={inputRef}
        type="file"
        multiple
        accept={accept}
        className="sr-only"
        onChange={(e) => {
          pick(e.target.files);
          e.target.value = ""; // allow re-selecting the same file
        }}
      />
    </div>
  );
}
