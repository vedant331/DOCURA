import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { type ReactElement } from "react";

import { StatusBadge } from "@/components/system/StatusBadge";
import { LoadingState, EmptyState, ErrorState, NotConnected } from "@/components/system/states";
import { ConfidenceIndicator } from "@/components/understanding/ConfidenceIndicator";
import { SensitivityBadge, SensitiveValue } from "@/components/understanding/SensitivityBadge";
import { ConflictPanel } from "@/components/understanding/ConflictPanel";
import { FieldList } from "@/components/forms/FieldList";
import { AmbiguityDialog } from "@/components/forms/AmbiguityDialog";
import { MatchingPanel } from "@/components/forms/MatchingPanel";
import { SensitiveApprovalDialog } from "@/components/forms/SensitiveApprovalDialog";
import { DeclarationWarning } from "@/components/forms/DeclarationWarning";
import { HandBackPanel } from "@/components/forms/HandBackPanel";
import type { AttributeValueResponse } from "@/lib/api";
import type { DetectedField, UploadFieldMatch } from "@/components/forms/types";

// These components are presentational seams (§33): they render only the props they are
// given and never fabricate backend data. The fixtures here are test inputs, not invented
// product data. SourceBadge/links require a router.
function r(ui: ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe("System status vocabulary (§28)", () => {
  it("renders a label + accessible text for a status (not colour alone)", () => {
    r(<StatusBadge status="conflict" />);
    expect(screen.getByText(/conflict/i)).toBeInTheDocument();
  });
});

describe("Global states (§29)", () => {
  it("renders loading, empty, error and not-connected", () => {
    const { rerender } = render(<LoadingState label="Loading things" />);
    expect(screen.getByRole("status")).toHaveTextContent(/loading things/i);
    rerender(<EmptyState title="Nothing here" />);
    expect(screen.getByText(/nothing here/i)).toBeInTheDocument();
    rerender(<ErrorState message="boom" />);
    expect(screen.getByRole("alert")).toHaveTextContent(/boom/i);
    rerender(<NotConnected title="Not wired" description="seam" />);
    expect(screen.getByText(/not wired/i)).toBeInTheDocument();
  });
});

describe("Confidence (§10)", () => {
  it("shows the real percentage and an honest 'no confidence' for null", () => {
    const { rerender } = render(<ConfidenceIndicator confidence={0.73} />);
    expect(screen.getByText(/73%/)).toBeInTheDocument();
    rerender(<ConfidenceIndicator confidence={null} />);
    expect(screen.getByText(/no confidence reported/i)).toBeInTheDocument();
  });
});

describe("Sensitivity (§14)", () => {
  it("masks sensitive values by default and reveals on action", () => {
    r(<SensitivityBadge tier="sensitive" />);
    expect(screen.getByText(/sensitive/i)).toBeInTheDocument();
    render(<SensitiveValue value="1234-5678" tier="sensitive" />);
    expect(screen.queryByText("1234-5678")).not.toBeInTheDocument(); // masked
    expect(screen.getByRole("button", { name: /reveal value/i })).toBeInTheDocument();
  });
});

describe("Conflict (§12)", () => {
  it("shows every candidate and never auto-resolves", () => {
    const attr: AttributeValueResponse = {
      canonical_identifier: "person.date_of_birth",
      value: null,
      is_ambiguous: true,
      observations: [
        { value: "1990-01-01", confidence: 0.8, document_id: "d1", extraction_run_id: "r1", page_number: 1, region: null },
        { value: "1991-01-01", confidence: 0.8, document_id: "d2", extraction_run_id: "r2", page_number: 1, region: null },
      ],
    };
    r(<ConflictPanel attribute={attr} />);
    expect(screen.getByText(/conflict detected/i)).toBeInTheDocument();
    expect(screen.getByText("1990-01-01")).toBeInTheDocument();
    expect(screen.getByText("1991-01-01")).toBeInTheDocument();
    expect(screen.getByText(/resolution not yet connected/i)).toBeInTheDocument();
  });
});

describe("Field interpretation (§19/§21/§25)", () => {
  it("renders matched/unknown/declaration field states; unknown stays untouched", () => {
    const fields: DetectedField[] = [
      { fieldId: "f1", type: "text", required: true, status: "matched", meaning: "Full name", proposedValue: "Vedant" },
      { fieldId: "f2", type: "text", required: false, status: "unknown" },
      { fieldId: "f3", type: "checkbox", required: true, status: "declaration", meaning: "I agree to terms", isDeclaration: true },
    ];
    r(<FieldList fields={fields} />);
    expect(screen.getByText(/full name/i)).toBeInTheDocument();
    expect(screen.getByText(/left untouched/i)).toBeInTheDocument();
    expect(screen.getByText(/you must decide/i)).toBeInTheDocument();
  });

  it("renders a standalone declaration warning", () => {
    r(<DeclarationWarning fieldLabel="I accept the privacy policy" />);
    expect(screen.getByText(/never accept, tick, or complete/i)).toBeInTheDocument();
  });
});

describe("Ambiguity (§20)", () => {
  it("offers candidates with no default selection", () => {
    r(
      <AmbiguityDialog
        open
        onOpenChange={() => {}}
        fieldLabel="Name"
        candidates={[{ value: "Vedant", source: "aadhaar.pdf" }, { value: "V. Kadam", source: "pan.pdf" }]}
      />,
    );
    const radios = screen.getAllByRole("radio");
    expect(radios).toHaveLength(2);
    expect(radios.every((el) => !(el as HTMLInputElement).checked)).toBe(true); // nothing pre-selected
  });
});

describe("Document matching (§22)", () => {
  it("shows multiple candidates and asks the user to choose", () => {
    const match: UploadFieldMatch = {
      fieldId: "upload_photo",
      requiredType: "image",
      status: "multiple",
      candidates: [
        { documentId: "d1", filename: "photo1.jpg", confidence: 0.6 },
        { documentId: "d2", filename: "photo2.jpg", confidence: 0.55 },
      ],
    };
    r(<MatchingPanel match={match} onChoose={() => {}} />);
    expect(screen.getByText(/multiple candidates/i)).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: /choose/i })).toHaveLength(2);
  });
});

describe("Sensitive approval (§24)", () => {
  it("shows what/where/why and no approve-all", () => {
    r(
      <SensitiveApprovalDialog
        open
        onOpenChange={() => {}}
        what="AB1234567"
        targetField="#passport"
        targetForm="Visa application"
        reason="The form asks for your passport number."
        onDecision={() => {}}
      />,
    );
    expect(screen.getByText(/only this one disclosure/i)).toBeInTheDocument();
    expect(screen.getByText(/visa application/i)).toBeInTheDocument();
    expect(screen.queryByText(/approve all/i)).not.toBeInTheDocument();
  });
});

describe("Hand-back (§27)", () => {
  it("states DOCURA does not submit, and shows unknown blockers honestly", () => {
    r(<HandBackPanel outstandingCount={null} handedBack={false} onHandBack={() => {}} />);
    expect(screen.getByText(/docura does not submit the form/i)).toBeInTheDocument();
    expect(screen.getByText(/blockers tracked in session/i)).toBeInTheDocument();
  });
});
