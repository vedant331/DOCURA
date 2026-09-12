import type { AttributeValueResponse } from "@/lib/api";
import { AttributeRow } from "@/components/record/AttributeRow";

// A titled group of attributes in the My Record view (§13), e.g. "Person" / "Qualification".
export function RecordSection({
  title,
  attributes,
  docNameById = {},
}: {
  title: string;
  attributes: AttributeValueResponse[];
  docNameById?: Record<string, string>;
}) {
  if (attributes.length === 0) return null;
  return (
    <section aria-labelledby={`record-${title}`} className="border border-border bg-surface/30">
      <h3 id={`record-${title}`} className="border-b border-border px-4 py-3 text-sm font-semibold text-foreground">
        {title}
      </h3>
      <div className="px-4">
        {attributes.map((a) => (
          <AttributeRow key={a.canonical_identifier} attribute={a} docNameById={docNameById} />
        ))}
      </div>
    </section>
  );
}
