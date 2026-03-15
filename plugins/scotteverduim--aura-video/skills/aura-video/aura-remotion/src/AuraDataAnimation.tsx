import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// ============================================================
// AURA CREATINE BRAND IDENTITY
// ============================================================
const BRAND = {
  // Colors
  bg: "#FAF8F5",           // Warm off-white (from product/photos)
  beige: "#E8E0D0",        // Warm beige accent
  sage: "#7A9E87",         // Sage green (from Kristina's outfit accents)
  dark: "#2C2C2C",         // Near-black for text
  white: "#FFFFFF",
  gold: "#C9A96E",         // Warm gold (from product jar label)

  // Typography — DM Sans (clean, modern, science-forward)
  fontFamily: "'DM Sans', 'Inter', sans-serif",
  fontWeightLight: 300,
  fontWeightRegular: 400,
  fontWeightBold: 700,
};

// ============================================================
// COMPONENT 1: STAT CARD
// Large number + label — e.g. "70%" + "less creatine in women"
// ============================================================
export const StatCard: React.FC<{
  stat: string;
  label: string;
  sublabel?: string;
}> = ({ stat, label, sublabel }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = spring({ frame, fps, config: { damping: 20 } });
  const slideUp = interpolate(fadeIn, [0, 1], [40, 0]);

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.bg, justifyContent: "center", alignItems: "center" }}>
      {/* Subtle background circle */}
      <div style={{
        position: "absolute",
        width: 400,
        height: 400,
        borderRadius: "50%",
        backgroundColor: BRAND.beige,
        opacity: 0.5,
      }} />

      {/* Content */}
      <div style={{
        transform: `translateY(${slideUp}px)`,
        opacity: fadeIn,
        textAlign: "center",
        zIndex: 1,
        padding: "0 60px",
      }}>
        {/* Big stat number */}
        <div style={{
          fontFamily: BRAND.fontFamily,
          fontWeight: BRAND.fontWeightBold,
          fontSize: 140,
          color: BRAND.sage,
          lineHeight: 1,
          letterSpacing: "-4px",
        }}>
          {stat}
        </div>

        {/* Label */}
        <div style={{
          fontFamily: BRAND.fontFamily,
          fontWeight: BRAND.fontWeightBold,
          fontSize: 36,
          color: BRAND.dark,
          marginTop: 16,
          lineHeight: 1.2,
          maxWidth: 500,
          margin: "16px auto 0",
        }}>
          {label}
        </div>

        {/* Sublabel */}
        {sublabel && (
          <div style={{
            fontFamily: BRAND.fontFamily,
            fontWeight: BRAND.fontWeightLight,
            fontSize: 22,
            color: BRAND.dark,
            opacity: 0.6,
            marginTop: 12,
          }}>
            {sublabel}
          </div>
        )}

        {/* Aura wordmark */}
        <div style={{
          fontFamily: BRAND.fontFamily,
          fontWeight: BRAND.fontWeightLight,
          fontSize: 18,
          color: BRAND.gold,
          letterSpacing: "6px",
          textTransform: "uppercase",
          marginTop: 40,
        }}>
          AURA CREATINE
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// COMPONENT 2: BAR CHART
// Two bars side by side — e.g. Women vs Men creatine levels
// ============================================================
export const BarChart: React.FC<{
  leftLabel: string;
  leftValue: number;   // 0-100
  rightLabel: string;
  rightValue: number;  // 0-100
  title: string;
}> = ({ leftLabel, leftValue, rightLabel, rightValue, title }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame, fps, config: { damping: 15, stiffness: 60 } });
  const leftHeight = interpolate(progress, [0, 1], [0, leftValue * 3]);
  const rightHeight = interpolate(progress, [0, 1], [0, rightValue * 3]);
  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.bg, justifyContent: "center", alignItems: "center" }}>
      <div style={{ opacity: fadeIn, width: "100%", padding: "0 80px", boxSizing: "border-box" }}>

        {/* Title */}
        <div style={{
          fontFamily: BRAND.fontFamily,
          fontWeight: BRAND.fontWeightBold,
          fontSize: 32,
          color: BRAND.dark,
          textAlign: "center",
          marginBottom: 60,
          lineHeight: 1.2,
        }}>
          {title}
        </div>

        {/* Bars */}
        <div style={{ display: "flex", justifyContent: "center", alignItems: "flex-end", gap: 60, height: 320 }}>
          {/* Left bar */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
            <div style={{
              fontFamily: BRAND.fontFamily,
              fontWeight: BRAND.fontWeightBold,
              fontSize: 28,
              color: BRAND.sage,
            }}>
              {leftValue}%
            </div>
            <div style={{
              width: 100,
              height: leftHeight,
              backgroundColor: BRAND.sage,
              borderRadius: "8px 8px 0 0",
            }} />
            <div style={{
              fontFamily: BRAND.fontFamily,
              fontWeight: BRAND.fontWeightRegular,
              fontSize: 20,
              color: BRAND.dark,
              textAlign: "center",
              maxWidth: 120,
            }}>
              {leftLabel}
            </div>
          </div>

          {/* Right bar */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
            <div style={{
              fontFamily: BRAND.fontFamily,
              fontWeight: BRAND.fontWeightBold,
              fontSize: 28,
              color: BRAND.gold,
            }}>
              {rightValue}%
            </div>
            <div style={{
              width: 100,
              height: rightHeight,
              backgroundColor: BRAND.gold,
              borderRadius: "8px 8px 0 0",
            }} />
            <div style={{
              fontFamily: BRAND.fontFamily,
              fontWeight: BRAND.fontWeightRegular,
              fontSize: 20,
              color: BRAND.dark,
              textAlign: "center",
              maxWidth: 120,
            }}>
              {rightLabel}
            </div>
          </div>
        </div>

        {/* Aura wordmark */}
        <div style={{
          fontFamily: BRAND.fontFamily,
          fontWeight: BRAND.fontWeightLight,
          fontSize: 16,
          color: BRAND.gold,
          letterSpacing: "6px",
          textTransform: "uppercase",
          textAlign: "center",
          marginTop: 40,
        }}>
          AURA CREATINE
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// COMPONENT 3: PERCENTAGE RING
// Animated circle filling up to a percentage
// ============================================================
export const PercentageRing: React.FC<{
  percentage: number;
  label: string;
  sublabel?: string;
}> = ({ percentage, label, sublabel }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame, fps, config: { damping: 18, stiffness: 50 } });
  const currentPct = interpolate(progress, [0, 1], [0, percentage]);
  const fadeIn = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  const size = 280;
  const strokeWidth = 18;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (currentPct / 100) * circumference;

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.bg, justifyContent: "center", alignItems: "center" }}>
      <div style={{ opacity: fadeIn, textAlign: "center" }}>
        {/* SVG Ring */}
        <div style={{ position: "relative", width: size, height: size, margin: "0 auto" }}>
          <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
            {/* Background ring */}
            <circle
              cx={size / 2} cy={size / 2} r={radius}
              fill="none" stroke={BRAND.beige} strokeWidth={strokeWidth}
            />
            {/* Progress ring */}
            <circle
              cx={size / 2} cy={size / 2} r={radius}
              fill="none" stroke={BRAND.sage} strokeWidth={strokeWidth}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
            />
          </svg>

          {/* Center text */}
          <div style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            textAlign: "center",
          }}>
            <div style={{
              fontFamily: BRAND.fontFamily,
              fontWeight: BRAND.fontWeightBold,
              fontSize: 64,
              color: BRAND.dark,
              lineHeight: 1,
            }}>
              {Math.round(currentPct)}%
            </div>
          </div>
        </div>

        {/* Label */}
        <div style={{
          fontFamily: BRAND.fontFamily,
          fontWeight: BRAND.fontWeightBold,
          fontSize: 30,
          color: BRAND.dark,
          marginTop: 24,
          maxWidth: 400,
          margin: "24px auto 0",
          lineHeight: 1.3,
        }}>
          {label}
        </div>

        {sublabel && (
          <div style={{
            fontFamily: BRAND.fontFamily,
            fontWeight: BRAND.fontWeightLight,
            fontSize: 20,
            color: BRAND.dark,
            opacity: 0.6,
            marginTop: 10,
          }}>
            {sublabel}
          </div>
        )}

        {/* Aura wordmark */}
        <div style={{
          fontFamily: BRAND.fontFamily,
          fontWeight: BRAND.fontWeightLight,
          fontSize: 16,
          color: BRAND.gold,
          letterSpacing: "6px",
          textTransform: "uppercase",
          marginTop: 32,
        }}>
          AURA CREATINE
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// COMPONENT 4: LOWER THIRD (Caption overlay)
// Minimal branded caption bar for bottom of video
// ============================================================
export const LowerThird: React.FC<{
  text: string;
}> = ({ text }) => {
  const frame = useCurrentFrame();
  const slideIn = spring({ frame, fps: 30, config: { damping: 20 } });
  const translateY = interpolate(slideIn, [0, 1], [80, 0]);

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 80 }}>
      <div style={{
        transform: `translateY(${translateY}px)`,
        backgroundColor: "rgba(250, 248, 245, 0.92)",
        paddingTop: 16,
        paddingBottom: 16,
        paddingLeft: 32,
        paddingRight: 32,
        borderRadius: 12,
        maxWidth: "85%",
        textAlign: "center",
        borderLeft: `4px solid ${BRAND.sage}`,
      }}>
        <div style={{
          fontFamily: BRAND.fontFamily,
          fontWeight: BRAND.fontWeightBold,
          fontSize: 28,
          color: BRAND.dark,
          lineHeight: 1.2,
        }}>
          {text}
        </div>
      </div>
    </AbsoluteFill>
  );
};
