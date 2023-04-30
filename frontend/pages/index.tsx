import Header from "./_header";
import HeatMap from "./_heatmap";
import ScatterPlot from "./_scatterPlot";
import WorldMap from "./_worldMap";

export default function Home() {
  return (
    <main>
      <Header />
      <WorldMap />
      <ScatterPlot />
      <HeatMap />
    </main>
  );
}
