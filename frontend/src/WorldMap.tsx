export default function WorldMap() {
    return (
        <div className="shadow m-8 p-8">
            <h1 className="text-xl mb-4">Choose your country of interest</h1>
            <div className="flex flex-col md:flex-row">
                <div className="md:w-7/12 max-md:mb-4">
                    <h2 className="bg-slate-50 max-md:h-96 h-full flex justify-center items-center font-light">
                        Map will be shown here...
                    </h2>
                </div>
                <div className="md:w-5/12">
                    <div className="grid columns-1 md:grid-cols-2 gap-4 pl-4">
                        <div className="shadow p-8 rounded-lg">
                            <p className="text-md font-light">Overall Happiness Score</p>
                            <p className="text-2xl font-bold my-2">8.2</p>
                            <p className="text-sm font-light">Rank 12 in the World</p>
                        </div>
                        <div className="shadow p-8 rounded-lg">
                            <p className="text-md font-light">Overall Happiness Score</p>
                            <p className="text-2xl font-bold my-2">8.2</p>
                            <p className="text-sm font-light">Rank 12 in the World</p>
                        </div>
                        <div className="shadow p-8 rounded-lg">
                            <p className="text-md font-light">Overall Happiness Score</p>
                            <p className="text-2xl font-bold my-2">8.2</p>
                            <p className="text-sm font-light">Rank 12 in the World</p>
                        </div>
                        <div className="shadow p-8 rounded-lg">
                            <p className="text-md font-light">Overall Happiness Score</p>
                            <p className="text-2xl font-bold my-2">8.2</p>
                            <p className="text-sm font-light">Rank 12 in the World</p>
                        </div>
                        <div className="shadow p-8 rounded-lg">
                            <p className="text-md font-light">Overall Happiness Score</p>
                            <p className="text-2xl font-bold my-2">8.2</p>
                            <p className="text-sm font-light">Rank 12 in the World</p>
                        </div>
                        <div className="shadow p-8 rounded-lg">
                            <p className="text-md font-light">Overall Happiness Score</p>
                            <p className="text-2xl font-bold my-2">8.2</p>
                            <p className="text-sm font-light">Rank 12 in the World</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
