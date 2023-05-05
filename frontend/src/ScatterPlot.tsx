export default function ScatterPlot() {
    return (
        <div className="shadow m-8 p-8">
            <div className="flex flex-col md:flex-row">
                <div className="md:w-4/12 max-md:mb-4 mx-4">
                    <h1 className="text-xl mb-4">Choose your two factors</h1>
                    <div className="rounded-xl shadow-sm hover:bg-slate-100 bg-slate-50 p-3 my-4">
                        <p className="text-lg font-light">Perception</p>
                        <p className="font-light">
                            Lorem ipsum dolor sit amet consectetur adipisicing elit.
                        </p>
                    </div>

                    <div className="rounded-xl shadow-sm hover:bg-slate-100 bg-slate-50 p-3 my-4">
                        <p className="text-lg font-light">Perception</p>
                        <p className="font-light">
                            Lorem ipsum dolor sit amet consectetur adipisicing elit.
                        </p>
                    </div>

                    <div className="rounded-xl shadow-sm hover:bg-slate-100 bg-slate-50 p-3 my-4">
                        <p className="text-lg font-light">Perception</p>
                        <p className="font-light">
                            Lorem ipsum dolor sit amet consectetur adipisicing elit.
                        </p>
                    </div>
                </div>
                <div className="md:w-4/12 max-md:mb-4 mx-4">
                    <h1 className="text-xl mb-4">In a nutshell</h1>
                    <div className="rounded-lg p-4 border-solid border-2 mb-4">
                        <p className="font-light text-lg">
                            The comparison shows: The{" "}
                            <span className="bg-green-100">higher</span> the perception of
                            corruption the <span className="bg-red-100">lower</span> the level
                            of life satisfaction in{" "}
                            <span className="bg-slate-100">Italy</span> between{" "}
                            <span className="bg-slate-100">2005 and 2007</span>.
                        </p>
                    </div>

                    <div className="rounded-lg p-4 border-solid border-2 grid columns-1 lg:grid-cols-2 gap-2">
                        <div>
                            <h1>Significance</h1>
                            <p className="font-light">
                                Lorem ipsum dolor sit amet consectetur adipisicing elit. Et enim
                                modi repellendus aliquid blanditiis eveniet, doloribus
                                perferendis vitae dolorem id voluptatum optio magnam cum eius
                                est nam iusto libero vel.
                            </p>
                        </div>
                        <div className="flex justify-center items-center ">
                            <h1 className="font-light uppercase">High Significance</h1>
                        </div>
                    </div>
                </div>
                <div className="md:w-4/12 max-md:mb-4 mx-4">
                    <h1 className="text-xl mb-4">In a graph</h1>
                    <h2 className="bg-slate-50 h-96 flex justify-center items-center font-light">
                        Graph will be shown here...
                    </h2>
                </div>
            </div>
        </div>
    );
}