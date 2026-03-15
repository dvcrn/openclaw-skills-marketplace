import { Composition } from "remotion";
import { StatCard, BarChart, PercentageRing, LowerThird } from "./AuraDataAnimation";

// 9:16 vertical format for TikTok/Reels
const WIDTH = 1080;
const HEIGHT = 1920;
const FPS = 30;
const DURATION_8S = 8 * FPS; // 240 frames

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* STAT CARD — e.g. "70% less creatine in women" */}
      <Composition
        id="StatCard"
        component={StatCard}
        durationInFrames={DURATION_8S}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={{
          stat: "70%",
          label: "less creatine in women",
          sublabel: "vs men at baseline",
        }}
      />

      {/* BAR CHART — e.g. Women vs Men creatine levels */}
      <Composition
        id="BarChart"
        component={BarChart}
        durationInFrames={DURATION_8S}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={{
          title: "Creatine stores",
          leftLabel: "Women",
          leftValue: 20,
          rightLabel: "Men",
          rightValue: 100,
        }}
      />

      {/* PERCENTAGE RING — e.g. "85% of women report improved focus" */}
      <Composition
        id="PercentageRing"
        component={PercentageRing}
        durationInFrames={DURATION_8S}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={{
          percentage: 85,
          label: "of women report improved focus",
          sublabel: "after 4 weeks of creatine",
        }}
      />

      {/* LOWER THIRD — caption overlay */}
      <Composition
        id="LowerThird"
        component={LowerThird}
        durationInFrames={DURATION_8S}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={{
          text: "Women have 70-80% less creatine",
        }}
      />
    </>
  );
};
