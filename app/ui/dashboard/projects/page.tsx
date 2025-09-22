import { getProjects } from '@/app/actions/actions';
import { ProjectTableClient } from './project-table-client';
import { Growth } from '@/app/lib/definitions';

export default async function ProjectTable() {
  // Fetch data on the server
  const projects = await getProjects();
  
  // Serialize dates for client transfer (Next.js requires serialization)
  const serializedProjects = projects.map(project => ({
    ...project,
    createdAt: project.createdAt.toISOString(),
    updatedAt: project.updatedAt.toISOString(),
  })) as unknown as Growth[];

  return (
    <div className="container mx-auto py-10">
      <div className="rounded-xl p-2">
        <ProjectTableClient initialData={serializedProjects} />
      </div>
    </div>
  );
}