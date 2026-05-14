import * as Cesium from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";
import "./style.css";

const ionToken = import.meta.env.VITE_ION_TOKEN;
const itwinShareKey = import.meta.env.VITE_ITWIN_SHARE_KEY;

const main = async () => {

  Cesium.Ion.defaultAccessToken = ionToken;
  Cesium.ITwinPlatform.defaultShareKey = itwinShareKey;
  
  const viewer = new Cesium.Viewer("cesiumContainer", {
    terrain: Cesium.Terrain.fromWorldTerrain(),
  });

  // Set the time for consistent lighting
  viewer.clock.currentTime = Cesium.JulianDate.fromDate(new Date(Date.UTC(2025, 7, 1, 7, 0, 0)));
  viewer.clock.shouldAnimate = false;

};

main().catch(console.error);
