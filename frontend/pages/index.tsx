import Header from "./_header";
import ScatterPlot from "./_scatterPlot";
import WorldMap from "./_worldMap";

export default function Home() {
  return (
    <main>
      <Header />
      <WorldMap />
      <ScatterPlot />
      <div className="shadow m-8 p-8">
        <h1 className="text-xl mb-4">Correlation Heat Map</h1>
        <h2 className="bg-slate-50 h-96 flex justify-center items-center font-light">
          Heatmap will be shown here...
        </h2>
      </div>
    </main>
  );
}
