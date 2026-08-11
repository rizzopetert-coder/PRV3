# /book/toc Fuller Vision — Concept Sketch

Status: Concept approved by Pete (2026-08-11). Not yet scoped for build — this captures the 
agreed direction so it survives context loss; a build scoping pass is a separate future step.

## Current state
/book/toc exists as a minimal hub (built this session, Category C): flat list of all 58 states 
using existing descriptive_prose, zero new content authored.

## 1. Clusters — color-coded filter tags
Two tag families, both existing data fields on each state:
- The 4 A's (primary_dimension: Aptitude / Authority / Alliance / Attitude)
- Signature (existing groupings, e.g. culture_erosion's 14+ states)

Filter UI: tag buttons at top of page, one color per dimension family (extend the locked visual 
identity palette — slate blue is the existing general-accent for taxonomy labels; dimension tags 
should get distinct treatment within that family, not clash with rust which stays reserved for 
Endemic severity only). Multi-select: OR within a tag family, AND across families.

PRE-BUILD CHECK: confirm whether primary_dimension currently exists on web/data/taxonomy.ts or 
only engine-side (engine/data/states.py). If frontend-absent, needs to be added — this is a 
plain taxonomy label already visible elsewhere in the app, not a scoring weight, so no P-03 
concern, just a data-completeness gap to close before the filter UI can work.

## 2. Media — linked, not duplicated
Reuses web/lib/book-state-index.ts (built this session, Category C) which already maps states 
to their /book pieces. Each /book/toc entry links out to:
- Any /book piece(s) referencing that state (buildable now)
- Citations/research backing that state's content (blocked on the still-deferred citation-
  sourcing workstream — link this in once that catches up, don't block the rest of the build 
  on it)

## 3. Intersection vectors — resolution_family as connective tissue
Approved direction: use resolution_family (existing field on every state, already indicates 
which service track resolves it — e.g. Intervention + Executive Advisory) as the primary 
mechanism connecting taxonomy browsing to services. Each state card shows a resolution_family 
badge linking to the relevant service page.

Explicitly deferred to a possible later phase, NOT part of this build: a richer interconnection 
graph/visualization between states. No existing data foundation supports that the way tags and 
resolution_family already do — would need its own separate design and scoping pass.

## Net result
/book/toc moves from a flat list to a filterable grid: dimension + signature tag filters at top, 
each state card showing description, tags, linked media, and a resolution_family badge pointing 
to the relevant service.

## Open items before this can be scoped for build
- primary_dimension frontend-availability check (see Pre-Build Check above)
- Actual build scoping (phased plan, file list, Gemini gate determination if any structural 
  changes are needed) — not done yet, this file is concept-level only
