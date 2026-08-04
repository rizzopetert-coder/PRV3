import { describe, it, expect } from "vitest";
import {
  AXES,
  KEYFRAMES,
  RESTING_FRAME,
  LIVE_CENTER,
  LIVE_MAX_R,
  computeFrame,
  dominantAxis,
  pointFor,
  pointsAttr,
  polarPoint,
  severityAccentTokens,
} from "./ConstellationField";

// Locks in the resting-frame geometry hand-verified during Stage 2 against
// the actual rendered SVG output (keyframe 0: apt .35, auth .30, all .25,
// att .30 -> vertices (450,250) (510,320) (450,370) (390,320)). Worth a
// permanent test specifically because this is math a future refactor
// could silently break with no visual or type-level signal — same
// category as the checkpoint splice logic, lower stakes.

describe("pointFor", () => {
  it("places each axis at weight * MAX_R along its angle, matching the hand-verified resting frame", () => {
    // Aptitude (top, -90deg), weight .35 -> r=70 -> (450, 320-70)
    expect(pointFor(0.35, AXES.apt)).toEqual({ x: 450, y: 250 });
    // Authority (right, 0deg), weight .30 -> r=60 -> (450+60, 320)
    expect(pointFor(0.3, AXES.auth)).toEqual({ x: 510, y: 320 });
    // Alliance (bottom, 90deg), weight .25 -> r=50 -> (450, 320+50)
    expect(pointFor(0.25, AXES.all)).toEqual({ x: 450, y: 370 });
    // Attitude (left, 180deg), weight .30 -> r=60 -> (450-60, 320)
    expect(pointFor(0.3, AXES.att)).toEqual({ x: 390, y: 320 });
  });
});

describe("computeFrame", () => {
  it("at keyframe 0 / t=0, produces the hand-verified resting weights and ring", () => {
    const frame = computeFrame(KEYFRAMES[0], KEYFRAMES[0], 0);
    expect(frame.w).toEqual({ apt: 0.35, auth: 0.3, all: 0.25, att: 0.3 });
    expect(frame.ring).toBe(0.0);
  });

  it("interpolates linearly at t=0.5 between two keyframes", () => {
    const kfA = { w: { apt: 0.0, auth: 0.0, all: 0.0, att: 0.0 }, ring: 0.0 };
    const kfB = { w: { apt: 1.0, auth: 1.0, all: 1.0, att: 1.0 }, ring: 2.0 };
    const frame = computeFrame(kfA, kfB, 0.5);
    expect(frame.w).toEqual({ apt: 0.5, auth: 0.5, all: 0.5, att: 0.5 });
    expect(frame.ring).toBe(1.0);
  });

  it("picks the dominant axis by current interpolated weight, not a static label", () => {
    const kfA = { w: { apt: 0.1, auth: 0.9, all: 0.1, att: 0.1 }, ring: 0 };
    const kfB = { w: { apt: 0.9, auth: 0.1, all: 0.1, att: 0.1 }, ring: 0 };
    expect(computeFrame(kfA, kfB, 0).domKey).toBe("auth");
    expect(computeFrame(kfA, kfB, 1).domKey).toBe("apt");
  });

  it("breaks ties in auth -> apt -> all -> att order, matching the reference mockup", () => {
    const allEqual = { apt: 0.5, auth: 0.5, all: 0.5, att: 0.5 };
    expect(computeFrame({ w: allEqual, ring: 0 }, { w: allEqual, ring: 0 }, 0).domKey).toBe(
      "auth",
    );
  });
});

describe("pointsAttr", () => {
  it("renders the resting frame as the exact hand-verified SVG points string", () => {
    expect(pointsAttr(RESTING_FRAME)).toBe("450,250 510,320 450,370 390,320");
  });
});

// --- Stage 3: live mode ------------------------------------------------

describe("severityAccentTokens", () => {
  it("uses the v1 rust token only for genuine Endemic severity", () => {
    expect(severityAccentTokens("Endemic")).toEqual({
      stroke: "var(--color-rust)",
      text: "var(--color-rust)",
    });
  });

  it("uses the v1 slate token for Entrenched", () => {
    expect(severityAccentTokens("Entrenched")).toEqual({
      stroke: "var(--color-slate)",
      text: "var(--color-slate)",
    });
  });

  it("uses the v1 slate token for Emerging", () => {
    expect(severityAccentTokens("Emerging")).toEqual({
      stroke: "var(--color-slate)",
      text: "var(--color-slate)",
    });
  });
});

describe("dominantAxis (live mode's static weights, not ambient's interpolated frame)", () => {
  it("picks the reference mockup's own dominant axis from its labeled weights", () => {
    // The results mockup's example: Authority 55%, Attitude 20%,
    // Aptitude 15%, Alliance 10% -> dominant is Authority.
    expect(dominantAxis({ apt: 0.15, auth: 0.55, all: 0.1, att: 0.2 })).toBe("auth");
  });

  it("breaks ties in auth -> apt -> all -> att order", () => {
    expect(dominantAxis({ apt: 0.5, auth: 0.5, all: 0.5, att: 0.5 })).toBe("auth");
    expect(dominantAxis({ apt: 0.5, auth: 0.1, all: 0.5, att: 0.5 })).toBe("apt");
    expect(dominantAxis({ apt: 0.1, auth: 0.1, all: 0.5, att: 0.5 })).toBe("all");
  });
});

describe("live-mode vertex geometry", () => {
  it("reproduces the results mockup's own example exactly (hand-verified against its rendered SVG)", () => {
    // mockup: apt .15, auth .55, all .10, att .20 -> polygon
    // "300,267 421,300 300,322 256,300"
    expect(polarPoint(0.15, AXES.apt, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 300, y: 267 });
    expect(polarPoint(0.55, AXES.auth, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 421, y: 300 });
    expect(polarPoint(0.1, AXES.all, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 300, y: 322 });
    expect(polarPoint(0.2, AXES.att, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 256, y: 300 });
  });
});
