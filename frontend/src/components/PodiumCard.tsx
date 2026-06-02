type PodiumCardProps = {
    position: 1 | 2 | 3;
    driverName: string;
    teamName: string;
    value: string;
    teamColor: string;
    image: string;
};

export function PodiumCard({
    position,
    driverName,
    teamName,
    value,
    teamColor,
    image,
}: PodiumCardProps) {
    const heights = {
        1: "h-[420px]",
        2: "h-[360px]",
        3: "h-[320px]",
    };

    return (
        <div
            className={`
                relative
                overflow-hidden
                rounded-2xl
                ${heights[position]}
            `}
            style={{
                backgroundColor: teamColor,
            }}
        >
            {/* Driver image */}
            <img
                src={image}
                alt={driverName}
                className="
                    absolute
                    bottom-0
                    right-0
                    h-[92%]
                    object-contain
                    pointer-events-none
                "
            />

            {/* Content */}
            <div className="relative z-10 flex h-full flex-col p-6">
                <div>
                    <div className="text-5xl font-bold text-white">
                        {position}
                    </div>

                    <h2 className="mt-4 text-4xl font-bold text-white leading-none">
                        {driverName}
                    </h2>

                    <p className="mt-2 text-lg text-white/80">
                        {teamName}
                    </p>
                </div>

                <div className="mt-auto">
                    <div className="text-4xl font-bold text-white">
                        {value}
                    </div>
                </div>
            </div>
        </div>
    );
}