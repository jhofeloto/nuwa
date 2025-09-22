import { fetchSpeciesByProjectId } from "@/app/lib/queries/queries";
import SimulateParamsForm from "./simulate-params-form";


export default async function SimulateComponent({ projectId }: { projectId?: string }) {
    let speciesList;
    if (projectId) {
        speciesList = await fetchSpeciesByProjectId(projectId);
    } else {
        return null;
    }

    return (
        <main>
                <SimulateParamsForm projectId={projectId} speciesList={speciesList} initialPopulationTable={[]} />
        </main>
    )


}